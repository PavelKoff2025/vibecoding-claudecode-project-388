"""Отправка сообщения в Telegram. Только стандартная библиотека."""
import os
import sys
import json
import urllib.request
import urllib.parse


def load_env(path=".env"):
    """Читает .env вручную, без python-dotenv."""
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def send(text: str) -> dict:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


if __name__ == "__main__":
    load_env()
    msg = sys.argv[1] if len(sys.argv) > 1 else "✅ Тест отправки через urllib"
    result = send(msg)
    print("OK" if result.get("ok") else result)
