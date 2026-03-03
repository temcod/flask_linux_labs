from __future__ import annotations

import shlex
import subprocess
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, request

from web.forms import RegistrationForm


def _flatten_form_errors(form_errors: Dict[str, List[str]]) -> List[str]:
    # WTForms возвращает ошибки в виде словаря {field: [messages]}.
    # Для ответа сервера часто удобнее иметь плоский список строк.
    errors: List[str] = []
    for field_name, field_errors in form_errors.items():
        for msg in field_errors:
            errors.append(f"{field_name}: {msg}")
    return errors


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)

    # SECRET_KEY обязателен для Flask-WTF (даже если CSRF отключён).
    # CSRF отключаем , чтобы проще тестировать через клиент/POSTMAN.
    app.config.update(
        SECRET_KEY="dev-secret-key",
        WTF_CSRF_ENABLED=False,
        TESTING=bool(testing),
    )

    @app.get("/")
    def index() -> str:
        return (
            "<h3>Practice 4</h3>"
            "<ul>"
            "<li>POST /registration</li>"
            "<li>GET /uptime</li>"
            "<li>GET /ps?arg=a&arg=u&arg=x</li>"
            "</ul>"
        )

   
    # Задача 1: /registration (валидация полей)
   
    @app.post("/registration")
    def registration() -> Response:
        # Принимаем данные либо как JSON, либо как обычную форму (x-www-form-urlencoded).
        if request.is_json:
            payload: Dict[str, Any] = request.get_json(silent=True) or {}
        else:
            payload = request.form.to_dict(flat=True)

        form = RegistrationForm(data=payload)

        # Если validate() не прошёл, возвращаем список ошибок и подробности по полям.
        if not form.validate():
            field_errors = form.errors
            errors_list = _flatten_form_errors(field_errors)
            return jsonify({"errors": errors_list, "field_errors": field_errors}), 400

        # Если всё ок — возвращаем данные обратно (для проверки через Postman удобно).
        return jsonify(
            {
                "status": "ok",
                "data": {
                    "email": form.email.data,
                    "phone": form.phone.data,
                    "name": form.name.data,
                    "address": form.address.data,
                    "index": form.index.data,
                    "comment": form.comment.data,
                },
            }
        )

   
    # Задача 4: /uptime
   
    @app.get("/uptime")
    def uptime() -> str:
        # Берём uptime через системную команду.
        # -p (pretty) даёт человекочитаемый формат: "up 3 hours, 2 minutes".
        command = ["uptime", "-p"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
        except Exception as exc:
            # Если вдруг uptime недоступен — вернём 500.
            return f"Current uptime is unknown ({exc})", 500

        pretty = (result.stdout or "").strip()

        # На всякий случай выкидываем префикс "up ", чтобы в ответе было только время.
        # В задании просили без лишней информации.
        pretty = pretty.removeprefix("up ").strip()
        return f"Current uptime is {pretty}"

    
    # Задача 5: /ps?arg=...
   
    @app.get("/ps")
    def ps_endpoint() -> str:
        # Аргументы приходят списком, например:
        # /ps?arg=a&arg=u&arg=x  -> args=['a','u','x'] -> ps a u x
        args: list[str] = request.args.getlist("arg")

        # вызываем subprocess без shell=True и передаём аргументы списком.
        # Так пользователь не сможет подсунуть "; rm -rf /" и т.п.
        command: list[str] = ["ps", *args]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            return "<pre>ps is not available</pre>", 500
        except Exception as exc:
            # Ошибку тоже заворачиваем в <pre>, чтобы в браузере читалось нормально.
            return f"<pre>Error: {shlex.quote(str(exc))}</pre>", 500

        out = (result.stdout or "") + (result.stderr or "")
        # Для удобного форматирования используем <pre>.
        return f"<pre>{out}</pre>"

    return app


if __name__ == "__main__":
    app = create_app(testing=False)
    app.run(host="127.0.0.1", port=5000, debug=True)
