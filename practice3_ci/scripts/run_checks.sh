#!/usr/bin/env bash
# Задача 5 (по желанию): система сборки для дешифратора
# 1) pylint -> JSON-файл + отчёт/score в консоль
# 2) unit-тесты
# 3) проверка кодов возврата

set -u

TARGET="cli/task3_decrypt.py"
JSON_OUT="pylint_report.json"

echo "== Pylint (JSON -> ${JSON_OUT}) =="
pylint --output-format=json "${TARGET}" > "${JSON_OUT}"
pylint_json_res=$?

echo
echo "== Pylint (report + score -> console) =="
pylint --reports=y --score=y "${TARGET}"
pylint_text_res=$?

echo
echo "== Unit tests (decryptor) =="
python3 -m unittest -v tests.test_task2_decryptor
tests_res=$?

echo
if [[ ${pylint_json_res} -eq 0 && ${pylint_text_res} -eq 0 && ${tests_res} -eq 0 ]]; then
  echo "OK"
  exit 0
else
  echo "Имеются ошибки"
  exit 1
fi
