#!/usr/bin/env python3
"""send.py — отправка сообщения в Telegram. Использование: python3 send.py "текст" """
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send(text: str) -> None:
    if not TOKEN or not CHAT_ID:
        print("⚠️  Не заданы TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID в .env")
        sys.exit(1)

    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True},
        timeout=15,
    )
    if r.status_code != 200:
        print(f"⚠️  Ошибка Telegram ({r.status_code}): {r.text}")
        sys.exit(1)
    print("Отправлено.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 send.py \"текст сообщения\"")
        sys.exit(1)
    send(sys.argv[1])
