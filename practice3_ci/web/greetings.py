from __future__ import annotations

from datetime import datetime
from typing import Tuple

# Готовый набор пожеланий по дням недели.
# Индексы соответствуют datetime.weekday(): 0 — понедельник, 6 — воскресенье.
WEEKDAY_WISHES: Tuple[str, ...] = (
    "Хорошего понедельника",
    "Хорошего вторника",
    "Хорошей среды",
    "Хорошего четверга",
    "Хорошей пятницы",
    "Хорошей субботы",
    "Хорошего воскресенья",
)


def get_weekday_wish() -> str:
    # Отдельная функция полезна для тестов: можно подменить/заморозить дату и проверять логику.
    weekday_idx = datetime.today().weekday()
    return WEEKDAY_WISHES[weekday_idx]


def get_username_with_weekdate(username: str) -> str:
    # Формируем фразу вида: "Привет, Хорошей субботы!"
    wish = get_weekday_wish()
    return f"Привет, {username}. {wish}!"
