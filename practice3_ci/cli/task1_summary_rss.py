"""
Задача 1. Список процессов

Функция get_summary_rss(path) читает файл с выводом `ps aux` и возвращает
суммарный RSS в человекочитаемом формате: B, KiB, MiB, ...

"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

# Набор единиц для вывода. Двигаемся по нему, пока число не станет меньше 1024.
UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")


def _humanize_bytes(num_bytes: int) -> str:
    # Переводим байты в "B / KiB / MiB / ...".
    # Делим на 1024, а не на 1000, потому что это двоичные единицы.
    value = float(num_bytes)  # float нужен, чтобы корректно делить и получать дроби
    unit_index = 0

    # Пока значение большое — укрупняем единицу.
    while value >= 1024.0 and unit_index < len(UNITS) - 1:
        value /= 1024.0
        unit_index += 1

    # Если получилось целое число — выводим без .00, иначе округляем до 2 знаков.
    if value.is_integer():
        return f"{int(value)} {UNITS[unit_index]}"
    return f"{value:.2f} {UNITS[unit_index]}"



def _iter_rss_values(lines: Iterable[str]) -> Iterable[int]:
    # Достаём RSS (6-й столбец) из каждой строки `ps aux`.
    # split() без аргументов нормально режет по любым пробелам.
    for line in lines:
        columns = line.split()

        # Формат может отличаться (локал/обрезанный вывод), поэтому проверяем длину.
        if len(columns) < 6:
            continue

        try:
            # RSS в задании считается в байтах, поэтому берём число как есть.
            yield int(columns[5])
        except ValueError:
            # Если в RSS попалось не число — просто пропускаем строку.
            continue



def get_summary_rss(ps_aux_output_path: str | Path) -> str:
    # Читаем файл целиком: для ps aux это нормально, он обычно небольшой.
    path = Path(ps_aux_output_path)
    with path.open("r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Первая строка — заголовок (USER PID %CPU ...), её не считаем.
    if lines:
        lines = lines[1:]

    total_rss_bytes = sum(_iter_rss_values(lines))
    return _humanize_bytes(total_rss_bytes)


if __name__ == "__main__":
    import sys

    # Путь к файлу выносим в переменную — так проще менять и читать код.
    if len(sys.argv) != 2:
        print("Usage: python3 cli/task1_summary_rss.py <ps_aux_output_file>")
        raise SystemExit(2)

    OUTPUT_FILE_PATH = sys.argv[1]
    print(get_summary_rss(OUTPUT_FILE_PATH))
