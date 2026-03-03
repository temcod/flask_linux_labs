from __future__ import annotations

# Форма регистрации для endpoint /registration.
# Используем Flask-WTF + WTForms, потому что так проще валидировать поля и получать список ошибок.

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import Email, InputRequired, NumberRange, Optional

from web.validators import NumberLength, number_length


class RegistrationForm(FlaskForm):
    # email: текст, обязателен, проверяем формат
    email = StringField(
        "email",
        validators=[
            InputRequired(message="Email is required."),  # поле обязательно
            Email(message="Invalid email format."),  # простая проверка вида user@host.tld
        ],
    )

    # phone: число, обязательно, только положительное, длина = 10 цифр
    phone = IntegerField(
        "phone",
        validators=[
            InputRequired(message="Phone is required."),
            NumberRange(min=0, message="Phone must be a positive number."),  # отрицательные не принимаем
            # Длина числа: используем свой валидатор из задания №2.
            # Тут показан вариант-функция. В validators.py ещё есть вариант-класс NumberLength.
            number_length(10, 10, message="Phone must be exactly 10 digits."),
        ],
    )

    # name: текст, обязателен
    name = StringField("name", validators=[InputRequired(message="Name is required.")])

    # address: текст, обязателен
    address = StringField("address", validators=[InputRequired(message="Address is required.")])

    # index: только числа, обязателен
    index = IntegerField("index", validators=[InputRequired(message="Index is required.")])

    # comment: текст, необязателен
    comment = StringField("comment", validators=[Optional()])
