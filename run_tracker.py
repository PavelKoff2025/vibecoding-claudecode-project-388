"""run_tracker.py — прогон: цены по urls.txt → last_run.json → коммит в tracker-data."""
import json
import sys

sys.path.insert(0, ".claude/skills/extract-price")
from extract_price import extract_price
from push_to_github import commit_run, check_config


def main():
    check_config()

    with open("urls.txt", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    table = []
    for url in urls:
        print(f"→ {url}")
        try:
            result = extract_price(url)
        except Exception as e:
            print(f"  ошибка: {e}")
            result = {"regular_price": None, "sale_price": None, "has_credit": False}
        table.append({"url": url, **result})

    with open("last_run.json", "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    print(f"✓ last_run.json ({len(table)} записей)")

    result = commit_run(table)
    commit = result["commit"]
    print(f"✅ Закоммичено: {result['content']['path']}  ({commit['sha'][:7]})")


if __name__ == "__main__":
    main()
