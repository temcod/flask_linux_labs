# Тесты для test_task1_good_day.py. Здесь проверяем задания практики 3 (unittest).

from __future__ import annotations

import unittest

from tests._freeze import freeze_time
from web.greetings import WEEKDAY_WISHES, get_username_with_weekdate


def extract_weekday_wish(message: str) -> str:
    """
    Отдельная функция нужна, чтобы тест не мог «случайно» пройти из‑за того,
    что в username уже есть название дня недели (пример: 'Хорошей среды').
    """
    # Берём то, что стоит после ПОСЛЕДНЕЙ '. ' и до '!'
    tail = message.rsplit('. ', 1)[-1]
    return tail.rstrip('!')


class GoodDayTests(unittest.TestCase):
    """Задача 1. Хорошего дня!"""

    def test_can_get_correct_username_with_weekdate(self) -> None:
        """Проверяем, что возвращается корректный день недели для каждого дня."""
        # Неделя 2026-02-09..2026-02-15: Пн..Вс
        dates = [
            ("2026-02-09", WEEKDAY_WISHES[0]),
            ("2026-02-10", WEEKDAY_WISHES[1]),
            ("2026-02-11", WEEKDAY_WISHES[2]),
            ("2026-02-12", WEEKDAY_WISHES[3]),
            ("2026-02-13", WEEKDAY_WISHES[4]),
            ("2026-02-14", WEEKDAY_WISHES[5]),
            ("2026-02-15", WEEKDAY_WISHES[6]),
        ]

        for date_str, expected_wish in dates:
            with self.subTest(date=date_str, expected=expected_wish):
                with freeze_time(date_str, patch_targets=["web.greetings.datetime"]):
                    message = get_username_with_weekdate("Петя")
                self.assertEqual(extract_weekday_wish(message), expected_wish)

    def test_username_can_contain_wish_phrase(self) -> None:
        """Если в username передали пожелание, тест всё равно проверяет ДЕНЬ недели."""
        with freeze_time("2026-02-09", patch_targets=["web.greetings.datetime"]):  # Monday
            message = get_username_with_weekdate("Хорошей среды")
        # Должно быть 'Хорошего понедельника', а не то, что было в username.
        self.assertEqual(extract_weekday_wish(message), WEEKDAY_WISHES[0])
