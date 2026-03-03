"""
Задачи 4–7: Flask приложение (Практика 2)

Endpoints:
- /hello-world/<name>                       (задача 4)
- /max_number/<path:numbers>                (задача 5)
- /preview/<int:size>/<path:relative_path>  (задача 6)
- /add/<date>/<int:number>                  (задача 7)
- /calculate/<int:year>                     (задача 7)
- /calculate/<int:year>/<int:month>         (задача 7)
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from flask import Flask, Response

app = Flask(__name__)

# Базовая директория проекта (чтобы относительные пути работали откуда бы ни запустили приложение).
BASE_DIR = Path(__file__).resolve().parent.parent


# Задача 4: /hello-world/<name>


# Храним названия дней недели в кортеже: он лёгкий и неизменяемый.
WEEKDAY_WISHES: Tuple[str, ...] = (
    "Хорошего понедельника",
    "Хорошего вторника",
    "Хорошей среды",
    "Хорошего четверга",
    "Хорошей пятницы",
    "Хорошей субботы",
    "Хорошего воскресенья",
)


# Задача 7: учёт финансов



class FinanceStorage:
    """Простое хранилище трат.

    Здесь держим три словаря:
    - daily:  по ключу 'YYYYMMDD' (быстро показать итог за день)
    - monthly: по ключу (year, month) (быстро показать итог за месяц)
    - yearly:  по ключу year (быстро показать итог за год)

    Так не приходится каждый раз пробегаться по всем дням и пересчитывать суммы.
    """

    daily: Dict[str, int]
    monthly: Dict[Tuple[int, int], int]
    yearly: Dict[int, int]

    def __init__(self) -> None:
        self.daily = {}
        self.monthly = {}
        self.yearly = {}

    def add(self, date_yyyymmdd: str, amount: int) -> int:
        # Дату уже проверили снаружи, поэтому тут просто режем строки.
        year = int(date_yyyymmdd[:4])
        month = int(date_yyyymmdd[4:6])

        # setdefault удобен тем, что не надо писать кучу if-ов.
        self.daily[date_yyyymmdd] = self.daily.setdefault(date_yyyymmdd, 0) + amount

        month_key = (year, month)
        self.monthly[month_key] = self.monthly.setdefault(month_key, 0) + amount

        self.yearly[year] = self.yearly.setdefault(year, 0) + amount

        return self.daily[date_yyyymmdd]


# Хранилище живёт в памяти процесса.
storage = FinanceStorage()


@app.get("/")
def index() -> Response:
    # подсказка по адресам.
    html = """<h2>Practice 2: Flask endpoints</h2>
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
    # weekday() возвращает 0..6 (Пн..Вс).
    weekday = datetime.today().weekday()
    wish = WEEKDAY_WISHES[weekday]
    text = f"Привет, {name}. {wish}!"
    return Response(text, mimetype="text/plain; charset=utf-8")



# Задача 5: /max_number/<path:numbers>


@app.get("/max_number/<path:numbers>")
def max_number(numbers: str) -> Response:
    # numbers приходит одной строкой, в ней числа разделены слешами.
    parts = [p for p in numbers.split("/") if p != ""]
    if not parts:
        return Response("Ошибка: не переданы числа.", status=400, mimetype="text/plain; charset=utf-8")

    parsed: list[int] = []
    for p in parts:
        try:
            parsed.append(int(p))
        except ValueError:
            # Если прилетело что-то вроде 'abc' — сразу объясняем пользователю.
            return Response(
                f"Ошибка: '{p}' не является целым числом.",
                status=400,
                mimetype="text/plain; charset=utf-8",
            )

    max_value = max(parsed)
    # По заданию число нужно выделить курсивом.
    html = f"Максимальное число: <i>{max_value}</i>"
    return Response(html, mimetype="text/html; charset=utf-8")



# Задача 6: /preview/<size>/<relative_path>


@app.get("/preview/<int:size>/<path:relative_path>")
def preview(size: int, relative_path: str) -> Response:
    if size < 0:
        return Response("Ошибка: SIZE должен быть неотрицательным.", status=400, mimetype="text/plain; charset=utf-8")

    # Собираем путь относительно корня проекта.
    # resolve() нужен, чтобы нормализовать '..' и получить абсолютный путь.
    target = (BASE_DIR / relative_path).resolve()
    base = BASE_DIR.resolve()

    # защита от обхода каталогов (например, ../../etc/passwd).
    try:
        target.relative_to(base)
    except ValueError:
        return Response("Ошибка: доступ к пути запрещён.", status=403, mimetype="text/plain; charset=utf-8")

    if not target.exists() or not target.is_file():
        return Response("Ошибка: файл не найден.", status=404, mimetype="text/plain; charset=utf-8")

    # читаем ровно size символов, а не весь файл.
    with target.open("r", encoding="utf-8", errors="replace") as f:
        preview_text = f.read(size)

    result_size = len(preview_text)
    html = f"<b>{target}</b> {result_size}<br>{preview_text}"
    return Response(html, mimetype="text/html; charset=utf-8")



# Задача 7: /add и /calculate


@app.get("/add/<date>/<int:number>")
def add_expense(date: str, number: int) -> Response:
    # Дата должна быть ровно 8 цифр (YYYYMMDD). Плюс дополнительно проверяем, что она реально существует.
    if len(date) != 8 or not date.isdigit():
        return Response("Ошибка: дата должна быть в формате YYYYMMDD.", status=400, mimetype="text/plain; charset=utf-8")
    try:
        datetime.strptime(date, "%Y%m%d")
    except ValueError:
        return Response("Ошибка: некорректная дата.", status=400, mimetype="text/plain; charset=utf-8")

    day_total = storage.add(date, number)
    return Response(
        f"Добавлено {number} руб. за {date}. Итого за день: {day_total} руб.",
        mimetype="text/plain; charset=utf-8",
    )


@app.get("/calculate/<int:year>")
def calculate_year(year: int) -> Response:
    # Если данных нет — возвращаем 0 (так проще пользователю).
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
