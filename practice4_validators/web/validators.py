from __future__ import annotations

# Свои валидаторы для WTForms.
# В задании нужно сделать 2 варианта:
#   1) функциональный валидатор (функция, которая возвращает проверяющую функцию)
#   2) валидатор-класс с методом __call__

from dataclasses import dataclass
from typing import Callable, Optional

from flask_wtf import FlaskForm
from wtforms.fields import Field
from wtforms.validators import ValidationError


def number_length(min: int, max: int, message: Optional[str] = None) -> Callable[[FlaskForm, Field], None]:
    """Функциональный валидатор длины числа.

    На вход: min/max — допустимая длина (в цифрах), message — текст ошибки.
    Возвращаем внутреннюю функцию, которую WTForms будет вызывать при validate().
    """
    if min < 0 or max < 0 or min > max:
        # Это скорее ошибка программиста, чем пользователя формы.
        raise ValueError("min and max must be non-negative and min <= max")

    def _number_length(form: FlaskForm, field: Field) -> None:
        value = field.data
        if value is None:
            # Если поле пустое, то за обязательность отвечает InputRequired/Optional.
            return

        # Превращаем в строку и убираем возможный минус.
        digits = str(value).lstrip("-")
        if not digits.isdigit():
            raise ValidationError(message or "Must be a number.")

        length = len(digits)
        if length < min or length > max:
            default_msg = f"Number length must be between {min} and {max} digits."
            raise ValidationError(message or default_msg)

    return _number_length


@dataclass(frozen=True)
class NumberLength:
    """Тот же валидатор, но в виде класса.

    Можно использовать так:
        IntegerField(validators=[InputRequired(), NumberLength(10, 10)])
    """

    min: int
    max: int
    message: Optional[str] = None

    def __post_init__(self) -> None:
        # Проверяем параметры на старте, чтобы потом не ловить странности во время validate().
        if self.min < 0 or self.max < 0 or self.min > self.max:
            raise ValueError("min and max must be non-negative and min <= max")

    def __call__(self, form: FlaskForm, field: Field) -> None:
        value = field.data
        if value is None:
            return

        digits = str(value).lstrip("-")
        if not digits.isdigit():
            raise ValidationError(self.message or "Must be a number.")

        length = len(digits)
        if length < self.min or length > self.max:
            default_msg = f"Number length must be between {self.min} and {self.max} digits."
            raise ValidationError(self.message or default_msg)
