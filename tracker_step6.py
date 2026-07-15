#!/usr/bin/env python3
"""Шаг 6 tracker: сравнение свежего прогона с предыдущим из tracker-data."""

import requests, json, base64, os, sys, subprocess
import re
from datetime import date
from dotenv import load_dotenv

load_dotenv()   # читаем .env

OWNER   = os.environ["GITHUB_OWNER"]
REPO    = os.environ.get("GITHUB_DATA_REPO", "tracker-data")
HEADERS = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}",
           "Accept": "application/vnd.github+json"}

def load_threshold(path="KNOWLEDGE.md", default=1.0):
    """Читает порог значимости (в %) из KNOWLEDGE.md.
    Ищет первое число перед знаком '%'. Если файла/числа нет — берёт default."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"⚠️  {path} не найден — использую порог по умолчанию {default}%")
        return default

    m = re.search(r"±?\s*(\d+(?:\.\d+)?)\s*%", text)
    if not m:
        print(f"⚠️  В {path} не найден порог в %, использую {default}%")
        return default

    value = float(m.group(1))
    print(f"ℹ️  Порог значимости загружен из {path}: ±{value}%")
    return value


PRICE_PCT_THRESHOLD = load_threshold()
API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"


def list_run_files() -> list[str]:
    r = requests.get(f"{API}/", headers=HEADERS); r.raise_for_status()
    return sorted(
        it["name"] for it in r.json()
        if it["name"].endswith(".json") and it["name"][:10].count("-") == 2
    )


def read_run(filename: str) -> list[dict]:
    r = requests.get(f"{API}/{filename}", headers=HEADERS); r.raise_for_status()
    return json.loads(base64.b64decode(r.json()["content"]).decode())


def get_previous_filename(today_file: str) -> str | None:
    prev = [f for f in list_run_files() if f < today_file]
    return prev[-1] if prev else None


def _pct_significant(old, new) -> bool:
    if old in (None, 0):
        return True
    return abs((new - old) / old * 100) >= PRICE_PCT_THRESHOLD


def compute_diff(prev, curr):
    prev_map = {i["url"]: i for i in prev}
    curr_map = {i["url"]: i for i in curr}
    events = []

    for url, cur in curr_map.items():
        old = prev_map.get(url)
        if old is None:
            events.append({"url": url, "type": "new_product", "significant": True})
            continue

        if old["regular_price"] != cur["regular_price"]:
            events.append({"url": url, "type": "regular_price_change",
                           "from": old["regular_price"], "to": cur["regular_price"],
                           "significant": _pct_significant(old["regular_price"], cur["regular_price"])})

        os_, ns_ = old.get("sale_price"), cur.get("sale_price")
        if os_ is None and ns_ is not None:
            events.append({"url": url, "type": "sale_started",
                           "from": None, "to": ns_, "significant": True})
        elif os_ is not None and ns_ is None:
            events.append({"url": url, "type": "sale_ended",
                           "from": os_, "to": None, "significant": True})
        elif os_ is not None and ns_ is not None and os_ != ns_:
            events.append({"url": url, "type": "sale_price_change",
                           "from": os_, "to": ns_, "significant": _pct_significant(os_, ns_)})

        if old.get("has_credit") != cur.get("has_credit"):
            events.append({"url": url,
                           "type": "credit_added" if cur["has_credit"] else "credit_removed",
                           "significant": True})

    for url in prev_map.keys() - curr_map.keys():
        events.append({"url": url, "type": "product_removed", "significant": True})

    return [e for e in events if e["significant"]]


LABELS = {
    "new_product": "🆕 новый товар", "product_removed": "❌ товар снят",
    "sale_started": "🔖 началась акция", "sale_ended": "🚫 акция закончилась",
    "sale_price_change": "🏷 изменилась цена по акции",
    "regular_price_change": "💰 изменилась обычная цена",
    "credit_added": "💳 появилась рассрочка", "credit_removed": "🚷 убрали рассрочку",
}

def render(events):
    if not events:
        print("Значимых изменений с прошлого прогона нет.")
        return
    print(f"Значимых изменений: {len(events)}\n")
    for e in events:
        line = f"{LABELS.get(e['type'], e['type'])}: {e['url']}"
        if "from" in e:
            line += f"  ({e['from']} → {e['to']})"
        print(line)

def build_telegram_text(prev_file, today_file, events):
    if not events:
        return None
    lines = [f"📊 Значимые изменения цен ({len(events)})",
             f"{prev_file} → {today_file}", ""]
    for e in events:
        line = f"{LABELS.get(e['type'], e['type'])}\n{e['url']}"
        if "from" in e:
            line += f"\n{e['from']} → {e['to']}"
        lines.append(line)
        lines.append("")
    return "\n".join(lines).strip()


def notify_telegram(text):
    if not text:
        print("ℹ️  Значимых изменений нет — Telegram-сообщение не отправляется.")
        return
    try:
        subprocess.run([sys.executable, "send.py", text], check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Не удалось отправить в Telegram (код {e.returncode}).")
    except FileNotFoundError:
        print("⚠️  send.py не найден рядом с трекером.")


def main():
    today_file = f"{date.today().isoformat()}.json"
    files = list_run_files()
    prev_file = get_previous_filename(today_file)

    if prev_file is None:
        print("Первый запуск — предыдущих прогонов нет, сравнивать не с чем.")
        return

    if today_file not in files:
        print(f"⚠️  Нет файла текущего прогона {today_file}. Сначала выполните шаг 5.")
        sys.exit(1)

    print(f"Сравнение: {prev_file} → {today_file}\n")
    events = compute_diff(read_run(prev_file), read_run(today_file))
    render(events)
    notify_telegram(build_telegram_text(prev_file, today_file, events))


if __name__ == "__main__":
    main()
