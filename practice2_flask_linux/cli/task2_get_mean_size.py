"""
Задача 2. Средний размер файла

берём вывод `ls -l` (обычно приходит через pipe),
вытаскиваем размеры обычных файлов и считаем среднее.

"""
from __future__ import annotations

import sys
from typing import Iterable


def _iter_file_sizes(lines: Iterable[str]) -> Iterable[int]:
    # Проходимся по строкам `ls -l` и отдаём размеры только обычных файлов.
    # В `ls -l` размер обычно стоит в 5-м столбце.
    for line in lines:
        line = line.rstrip("\n")
        if not line:
            continue

        # Первая строка вида `total 123` — это не файл.
        if line.startswith("total "):
            continue

        # split(maxsplit=8) — чтобы имя файла (особенно с пробелами) не разваливало парсинг.
        parts = line.split(maxsplit=8)
        if len(parts) < 5:
            # Если строка какая-то странная — пропускаем.
            continue

        perms = parts[0]
        # Каталоги/ссылки/устройства нас не интересуют: берём только строки, начинающиеся с '-'.
        if not perms.startswith("-"):
            continue

        try:
            yield int(parts[4])
        except ValueError:
            # Если размер не число — просто не учитываем.
            continue


def get_mean_size(ls_l_output: str) -> float:
    # На вход приходит весь текст. Дальше раскладываем на строки и парсим.
    sizes = list(_iter_file_sizes(ls_l_output.splitlines()))

    # Если файлов нет (или не удалось достать размеры) — по заданию возвращаем 0.
    if not sizes:
        return 0.0

    return sum(sizes) / len(sizes)


if __name__ == "__main__":
    # stdin читаем целиком: вывод ls -l маленький, так проще.
    data = sys.stdin.read()
    mean_size = get_mean_size(data)

    # Для удобства: если получилось целое число — печатаем без дробной части.
    if float(mean_size).is_integer():
        print(int(mean_size))
    else:
        print(f"{mean_size:.2f}")
