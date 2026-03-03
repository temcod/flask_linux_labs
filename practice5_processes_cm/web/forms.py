from __future__ import annotations

# Форма для endpoint /execute.
# Поля:
#   code    — python-код строкой
#   timeout — ограничение по времени (1..30 секунд)

from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class ExecuteCodeForm(FlaskForm):
    # Код ограничиваем по длине, чтобы не прислали мегабайты текста.
    code = TextAreaField(
        "code",
        validators=[
            DataRequired(message="code is required"),
            Length(max=10_000, message="code is too long"),
        ],
    )

    # Таймаут строго по заданию: положительное число, не больше 30.
    timeout = IntegerField(
        "timeout",
        validators=[
            DataRequired(message="timeout is required"),
            NumberRange(min=1, max=30, message="timeout must be between 1 and 30 seconds"),
        ],
    )
