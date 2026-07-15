#!/usr/bin/env python3
"""Тест шага 6: правим прошлый прогон, чтобы проверить фильтр значимости."""
import requests, json, base64, os
from dotenv import load_dotenv

load_dotenv()
OWNER   = os.environ["GITHUB_OWNER"]
REPO    = os.environ.get("GITHUB_DATA_REPO", "tracker-data")
HEADERS = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}",
           "Accept": "application/vnd.github+json"}
FNAME   = "2026-07-14.json"
url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FNAME}"

r = requests.get(url, headers=HEADERS); r.raise_for_status()
sha  = r.json()["sha"]
data = json.loads(base64.b64decode(r.json()["content"]).decode())

if len(data) >= 2:
    data[0]["regular_price"] = round(data[0]["regular_price"] * 0.90)  # рост >1% -> ЗНАЧИМОЕ
    data[1]["regular_price"] = data[1]["regular_price"] + 2            # <1% -> ОТСЕВ
    print(f"[0] {data[0]['url']} -> {data[0]['regular_price']} (ждём ЗНАЧИМОЕ)")
    print(f"[1] {data[1]['url']} -> {data[1]['regular_price']} (ждём ОТСЕВ)")

payload = {
    "message": "test: adjust previous run prices for step6 diff check",
    "content": base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode()).decode(),
    "sha": sha,
}
resp = requests.put(url, headers=HEADERS, json=payload); resp.raise_for_status()
print("✅ prev run updated — теперь запусти: python3 tracker_step6.py")
