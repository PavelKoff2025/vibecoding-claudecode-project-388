import json
from datetime import date, timedelta
from push_to_github import commit_run

with open("last_run.json", encoding="utf-8") as f:
    data = json.load(f)

yesterday = (date.today() - timedelta(days=1)).isoformat()
print(f"→ Тестовый коммит под датой: {yesterday}")

result = commit_run(data, run_date=yesterday)
print(f"✅ Закоммичено: {result['content']['path']}")
