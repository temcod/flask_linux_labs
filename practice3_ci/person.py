from __future__ import annotations

import datetime


class Person:
    """Простой класс из задания «Доверяй, но проверяй».

    Тут  оставлен минимальный набор полей и методов, чтобы их можно было
    нормально покрыть тестами и поймать типичные ошибки (формула возраста, присваивания и т.д.).
    """

    def __init__(self, name: str, year_of_birth: int, address: str = "") -> None:
        # name — имя человека
        # yob  — год рождения (year of birth)
        # address может быть пустым: это значит «адрес не указан»
        self.name = name
        self.yob = year_of_birth
        self.address = address

    def get_age(self) -> int:
        # Возраст считаем как текущий год минус год рождения.
        # В месяцы/дни тут не углубляемся, по заданию это не нужно.
        now = datetime.datetime.now()
        return now.year - self.yob

    def get_name(self) -> str:
        # Просто возвращаем имя (геттер).
        return self.name

    def set_name(self, name: str) -> None:
        # Меняем имя на новое.
        self.name = name

    def set_address(self, address: str) -> None:
        # Меняем адрес на новый.
        self.address = address

    def get_address(self) -> str:
        # Возвращаем текущий адрес.
        return self.address

    def is_homeless(self) -> bool:
        """True, если адрес не задан.

        Считаем, что адрес не задан, когда это пустая строка или None.
        """
        return not self.address
