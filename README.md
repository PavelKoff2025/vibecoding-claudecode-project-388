# Трекер цен на книги («Читай-город»)

Учебный проект курса по вайбкодингу.

## О проекте
Отслеживает цены на книги в магазине chitai-gorod.ru:
обычную цену, цену по скидке и наличие рассрочки.

## ⚠️ Про инструменты
Аккаунт Anthropic заблокирован без возможности восстановления,
поэтому логика Claude Code (skill `extract-price`, MCP-интеграция)
реализуется на чистом Python.

## Структура
- `.claude/skills/extract-price/` — заготовка скилла извлечения цены
- `urls.txt` — список отслеживаемых товаров

---

### Hexlet tests and linter status:
[![Actions Status](https://github.com/PavelKoff2025/vibecoding-claudecode-project-388/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/PavelKoff2025/vibecoding-claudecode-project-388/actions)
