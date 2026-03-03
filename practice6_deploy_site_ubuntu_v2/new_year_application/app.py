
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from flask import Flask, abort, render_template, send_file
from werkzeug.utils import safe_join


def days_until_new_year(today: date | None = None) -> int:
    # Считаем, сколько дней осталось до 1 января следующего года.
    # today можно передать вручную (удобно для тестов), иначе берём текущую дату.
    today = today or date.today()
    target = date(today.year + 1, 1, 1)
    return (target - today).days


def create_app() -> Flask:
    # static_folder=None — отключаем стандартную раздачу статики Flask,
    # потому что по заданию нужно сделать свой endpoint /static/...
    app = Flask(__name__, static_folder=None)

    # Папка со статикой (css/js/images) — лежит рядом с app.py
    static_directory = Path(__file__).resolve().parent / "static"
    app.config["STATIC_DIRECTORY"] = str(static_directory)

    @app.get("/")
    def index():
        # Шаблон index.html находится в templates/.
        return render_template("index.html", days_left=days_until_new_year())

    @app.get("/static/<path:relative_path>")
    def send_static(relative_path: str):
        # Отдаём любой файл из папки static по URL /static/...
        # safe_join защищает от path traversal (../../etc/passwd и подобное).
        root_dir = app.config["STATIC_DIRECTORY"]
        safe_path = safe_join(root_dir, relative_path)
        if safe_path is None:
            abort(404)
        if not os.path.isfile(safe_path):
            abort(404)
        return send_file(safe_path)

    return app


if __name__ == "__main__":
    # На сервере удобно слушать 0.0.0.0, чтобы сайт был доступен снаружи.
    create_app().run(host="0.0.0.0", port=8000, debug=False)
