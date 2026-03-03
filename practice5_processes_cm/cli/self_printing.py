from __future__ import annotations

# Доп.задача: «самопечать».
# Скрипт должен вывести свой же исходник. Самый надёжный вариант — читать __file__.

from pathlib import Path


def main() -> None:
    # resolve() нужен, чтобы получить абсолютный путь (скрипт может запускаться из любой папки).
    script_path = Path(__file__).resolve()

    # Печатаем файл как есть. end="" — чтобы не добавлять лишний перевод строки.
    print(script_path.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
