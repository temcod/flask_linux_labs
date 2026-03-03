from __future__ import annotations

import argparse
from typing import Any

from flask import Flask, jsonify, request

from web.executor import execute_python_code
from web.forms import ExecuteCodeForm


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)

    # SECRET_KEY нужен для Flask-WTF.
    # CSRF выключаем, потому что это учебный endpoint и так проще тестировать.
    app.config.update(
        SECRET_KEY="dev-secret-key",
        WTF_CSRF_ENABLED=False,
    )
    if config:
        app.config.update(config)

    @app.get("/")
    def index():
        return (
            "Practice 5 is running. Use POST /execute with form fields "
            "'code' and 'timeout'."
        )

    # Задача 2: удалённое исполнение кода (POST).
    @app.post("/execute")
    def execute():
        # Создаём форму и подсовываем ей request.form.
        # meta={'csrf': False} — чтобы гарантированно не требовался CSRF даже в тестах.
        form = ExecuteCodeForm(meta={"csrf": False})
        form.process(data=request.form)

        # Если входные данные не прошли валидацию — возвращаем ошибки.
        if not form.validate():
            return jsonify({"ok": False, "errors": form.errors}), 400

        # Выполняем код в отдельном процессе.
        result = execute_python_code(form.code.data, int(form.timeout.data))

        # Отдельный флаг timed_out, чтобы клиенту было понятно, что случилось.
        if result.timed_out:
            return jsonify(
                {
                    "ok": True,
                    "timed_out": True,
                    "message": "Execution did not finish within the given timeout.",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            )

        return jsonify(
            {
                "ok": True,
                "timed_out": False,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        )

    return app


def main() -> None:
    # Отдельный main, чтобы можно было запускать сервер с разным портом.
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    app = create_app()
    app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
