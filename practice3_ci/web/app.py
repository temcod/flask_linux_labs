"""Practice 2/3: Flask приложение.

Это тот же набор endpoint, что и в практике 2, просто в практике 3
к ним добавляются тесты (и часть логики вынесена в отдельные функции
для удобства тестирования).

Endpoints:
- /hello-world/<name>
- /max_number/<path:numbers>
- /preview/<int:size>/<path:relative_path>
- /add/<date>/<int:number>
- /calculate/<int:year>
- /calculate/<int:year>/<int:month>
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from flask import Flask, Response

from .greetings import get_username_with_weekdate

app = Flask(__name__)

# Базовая директория проекта (используем для превью файлов).
BASE_DIR = Path(__file__).resolve().parent.parent


class FinanceStorage:
    """Хранилище трат в памяти.

    В тестах постоянно сбрасываем storage, поэтому тут есть метод clear().
    """

    daily: Dict[str, int]
    monthly: Dict[Tuple[int, int], int]
    yearly: Dict[int, int]

    def __init__(self) -> None:
        self.daily = {}
        self.monthly = {}
        self.yearly = {}

    def clear(self) -> None:
        # Удобно для тестов: возвращаемся к пустому состоянию перед каждым кейсом.
        self.daily.clear()
        self.monthly.clear()
        self.yearly.clear()

    def add(self, date_yyyymmdd: str, amount: int) -> int:
        year = int(date_yyyymmdd[:4])
        month = int(date_yyyymmdd[4:6])

        # Суммируем сразу в нескольких разрезах, чтобы /calculate работал быстро.
        self.daily[date_yyyymmdd] = self.daily.setdefault(date_yyyymmdd, 0) + amount

        month_key = (year, month)
        self.monthly[month_key] = self.monthly.setdefault(month_key, 0) + amount

        self.yearly[year] = self.yearly.setdefault(year, 0) + amount

        return self.daily[date_yyyymmdd]


storage = FinanceStorage()


@app.get("/")
def index() -> Response:
    # Подсказка по адресу — удобно в браузере.
    html = """<h2>Practice 2/3: Flask endpoints</h2>
<ul>
  <li>/hello-world/&lt;name&gt;</li>
  <li>/max_number/&lt;numbers separated by /&gt; (пример: /max_number/10/2/9/1)</li>
  <li>/preview/&lt;size&gt;/&lt;relative_path&gt; (пример: /preview/8/docs/simple.txt)</li>
  <li>/add/&lt;YYYYMMDD&gt;/&lt;amount&gt; (пример: /add/20260214/150)</li>
  <li>/calculate/&lt;year&gt; (пример: /calculate/2026)</li>
  <li>/calculate/&lt;year&gt;/&lt;month&gt; (пример: /calculate/2026/2)</li>
</ul>
"""
    return Response(html, mimetype="text/html; charset=utf-8")


@app.get("/hello-world/<name>")
def hello_world(name: str) -> Response:
    # Логику формирования текста вынесли в greetings.py, чтобы её можно было отдельно тестировать.
    text = get_username_with_weekdate(name)
    return Response(text, mimetype="text/plain; charset=utf-8")


@app.get("/max_number/<path:numbers>")
def max_number(numbers: str) -> Response:
    parts = [p for p in numbers.split("/") if p != ""]
    if not parts:
        return Response("Ошибка: не переданы числа.", status=400, mimetype="text/plain; charset=utf-8")

    parsed: list[int] = []
    for p in parts:
        try:
            parsed.append(int(p))
        except ValueError:
            return Response(
                f"Ошибка: '{p}' не является целым числом.",
                status=400,
                mimetype="text/plain; charset=utf-8",
            )

    max_value = max(parsed)
    html = f"Максимальное число: <i>{max_value}</i>"
    return Response(html, mimetype="text/html; charset=utf-8")


@app.get("/preview/<int:size>/<path:relative_path>")
def preview(size: int, relative_path: str) -> Response:
    if size < 0:
        return Response("Ошибка: SIZE должен быть неотрицательным.", status=400, mimetype="text/plain; charset=utf-8")

    target = (BASE_DIR / relative_path).resolve()
    base = BASE_DIR.resolve()

    # Защита от выхода за пределы проекта через '..'.
    try:
        target.relative_to(base)
    except ValueError:
        return Response("Ошибка: доступ к пути запрещён.", status=403, mimetype="text/plain; charset=utf-8")

    if not target.exists() or not target.is_file():
        return Response("Ошибка: файл не найден.", status=404, mimetype="text/plain; charset=utf-8")

    with target.open("r", encoding="utf-8", errors="replace") as f:
        # Читаем только первые size символов.
        preview_text = f.read(size)

    result_size = len(preview_text)
    html = f"<b>{target}</b> {result_size}<br>{preview_text}"
    return Response(html, mimetype="text/html; charset=utf-8")


@app.get("/add/<date>/<int:number>")
def add_expense(date: str, number: int) -> Response:
    # В практике 3 по заданию нужно добиться ситуации,
    # когда при невалидной дате endpoint «падает» с ошибкой.
    # Поэтому тут НЕТ try/except: datetime.strptime сам бросит ValueError,
    # а в режиме TESTING=True это исключение пробросится в тест.
    datetime.strptime(date, "%Y%m%d")

    # Если дата валидная — спокойно добавляем трату.
    day_total = storage.add(date, number)
    return Response(
        f"Добавлено {number} руб. за {date}. Итого за день: {day_total} руб.",
        mimetype="text/plain; charset=utf-8",
    )


@app.get("/calculate/<int:year>")
def calculate_year(year: int) -> Response:
    total = storage.yearly.get(year, 0)
    return Response(f"Суммарные траты за {year} год: {total} руб.", mimetype="text/plain; charset=utf-8")


@app.get("/calculate/<int:year>/<int:month>")
def calculate_month(year: int, month: int) -> Response:
    if month < 1 or month > 12:
        return Response("Ошибка: month должен быть от 1 до 12.", status=400, mimetype="text/plain; charset=utf-8")
    total = storage.monthly.get((year, month), 0)
    return Response(f"Суммарные траты за {year}-{month:02d}: {total} руб.", mimetype="text/plain; charset=utf-8")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
