cd vibecoding-claudecode-project-388

# SKILL.md
nano .claude/skills/extract-price/SKILL.md      # вставь содержимое из блока 1

# extract_price.py
nano .claude/skills/extract-price/extract_price.py   # вставь код из блока 2

# зависимости
echo -e "requests\nbeautifulsoup4" > requirements.txt

git add .
git commit -m "Скилл extract-price: SKILL.md + Python-реализация"
git push
