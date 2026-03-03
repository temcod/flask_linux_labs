#!/usr/bin/env bash
# Мини-скрипт для проверки практики:
# 1) запускаем юнит-тесты
# 2) если всё ок — печатаем OK

set -euo pipefail  # падаем на первой ошибке, не используем неинициализированные переменные

python3 -m unittest discover -s tests -v
echo "OK: tests passed"
