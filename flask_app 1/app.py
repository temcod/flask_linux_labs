

import os
import random
import re
from datetime import datetime, timedelta

from flask import Flask


# Список машин — не пересоздаётся при каждом запросе
CARS = ["Chevrolet", "Renault", "Ford", "Lada"]

# Список пород кошек - константа
CATS = [
    "корниш-рекс",
    "русская голубая",
    "шотландская вислоухая",
    "мейн-кун",
    "манчкин",
]

# Путь к файлу "Война и мир" — делаем абсолютный, чтобы запуск из любой папки работал
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_FILE = os.path.join(BASE_DIR, "war_and_peace.txt")


def load_words_from_book() -> list[str]:
    """Читаем книгу и вытаскиваем из неё слова.

    Убираем знаки препинания и лишние символы.
    Функцию вызываем один раз при старте сервера.
    """

    if not os.path.exists(BOOK_FILE):
        # Если файл не найден — по условию возвращаем заглушку
        return ["слово"]

    with open(BOOK_FILE, "r", encoding="utf-8") as file:
        text = file.read()

    # Оставляем только буквы и пробелы (всё остальное меняем на пробелы)
    # Так потом split() нормально разделит на слова.
    clean_text = re.sub(r"[^а-яА-Яa-zA-Z\s]", " ", text)

    # Разбиваем на слова и убираем пустые элементы
    return [word for word in clean_text.split() if word]


# Загружаем слова один раз при запуске
WAR_AND_PEACE_WORDS = load_words_from_book()



# Flask-приложение


app = Flask(__name__)


@app.route("/hello_world")
def hello_world() -> str:
    # Самый базовый эндпоинт: возвращаем обычную строку
    return "Привет, мир!"


@app.route("/cars")
def cars() -> str:
    # Возвращаем строку с машинами через запятую
    return ", ".join(CARS)


@app.route("/cats")
def cats() -> str:
    # Возвращаем случайную породу кошки
    return random.choice(CATS)


@app.route("/get_time/now")
def get_time_now() -> str:
    # Текущее время в понятном формате
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Точное время: {current_time}"


@app.route("/get_time/future")
def get_time_future() -> str:
    # Время через час 
    future_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    return f"Точное время через час будет {future_time}"


@app.route("/get_random_word")
def get_random_word() -> str:
    # Слово выбирается случайно, но файл не читается повторно
    return random.choice(WAR_AND_PEACE_WORDS)


@app.route("/counter")
def counter() -> str:
    """Счётчик посещений.

    По требованию: счётчик хранится как атрибут функции.
    """

    counter.visits += 1
    return str(counter.visits)


# Инициализация счётчика (атрибут функции)
counter.visits = 0


if __name__ == "__main__":
    # debug=True - авто-перезапуск и подробные ошибки
    app.run(debug=True)

# Примеры:
# http://127.0.0.1:5000/hello_world
# http://127.0.0.1:5000/cars
# http://127.0.0.1:5000/cats
# http://127.0.0.1:5000/get_time/now
# http://127.0.0.1:5000/get_time/future
# http://127.0.0.1:5000/get_random_word
# http://127.0.0.1:5000/counter
