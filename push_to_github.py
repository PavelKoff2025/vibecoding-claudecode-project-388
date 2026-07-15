"""Коммитит файл прогона YYYY-MM-DD.json в приватный репозиторий tracker-data
через GitHub REST API (Contents API). Аналог поведения GitHub MCP:
запись файла = отдельный коммит, без локального git clone/push.
"""
import os
import sys
import json
import base64
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_DATA_REPO", "tracker-data")

API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def check_config():
    missing = [k for k, v in {"GITHUB_TOKEN": TOKEN, "GITHUB_OWNER": OWNER}.items() if not v]
    if missing:
        sys.exit(f"Не заданы переменные окружения: {', '.join(missing)} (см. .env)")


def get_existing_sha(path: str):
    """Если файл за сегодня уже есть — нужен его sha для обновления (иначе 409)."""
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        return r.json()["sha"]
    if r.status_code == 404:
        return None
    r.raise_for_status()


def commit_run(data: list, run_date: str | None = None) -> dict:
    filename = f"{run_date or date.today().isoformat()}.json"
    content = json.dumps(data, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")

    payload = {
        "message": f"tracker run {filename}",
        "content": encoded,
    }
    sha = get_existing_sha(filename)
    if sha:
        payload["sha"] = sha  # перезапись прогона за сегодня

    url = f"{API}/repos/{OWNER}/{REPO}/contents/{filename}"
    r = requests.put(url, headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        sys.exit(f"Ошибка коммита ({r.status_code}): {r.text}")
    return r.json()


def main():
    check_config()
    with open("last_run.json", encoding="utf-8") as f:
        data = json.load(f)

    result = commit_run(data)
    commit = result["commit"]
    print(f"✅ Закоммичено: {result['content']['path']}")
    print(f"   commit: {commit['sha'][:7]}  {commit['html_url']}")


if __name__ == "__main__":
    main()
