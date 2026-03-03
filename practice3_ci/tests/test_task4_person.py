# Тесты для test_task4_person.py. Здесь проверяем задания практики 3 (unittest).

from __future__ import annotations

import unittest

from person import Person
from tests._freeze import freeze_time


class PersonTests(unittest.TestCase):
    """Задача 4. Доверяй, но проверяй — тесты на каждый метод класса Person."""

    def test_init_sets_fields(self) -> None:
        p = Person("Ivan", 2000, "Ekaterinburg")
        self.assertEqual(p.get_name(), "Ivan")
        self.assertEqual(p.get_address(), "Ekaterinburg")

    def test_get_age_returns_correct_age(self) -> None:
        p = Person("Ivan", 2000)
        with freeze_time("2026-02-14", patch_targets=["person.datetime.datetime"]):
            self.assertEqual(p.get_age(), 26)

    def test_get_name(self) -> None:
        p = Person("Ivan", 2000)
        self.assertEqual(p.get_name(), "Ivan")

    def test_set_name(self) -> None:
        p = Person("Ivan", 2000)
        p.set_name("Petr")
        self.assertEqual(p.get_name(), "Petr")

    def test_set_address_and_get_address(self) -> None:
        p = Person("Ivan", 2000)
        p.set_address("Moscow")
        self.assertEqual(p.get_address(), "Moscow")

    def test_is_homeless_true_when_empty(self) -> None:
        p = Person("Ivan", 2000, "")
        self.assertTrue(p.is_homeless())

    def test_is_homeless_false_when_address_set(self) -> None:
        p = Person("Ivan", 2000, "Moscow")
        self.assertFalse(p.is_homeless())

    def test_is_homeless_true_when_none(self) -> None:
        p = Person("Ivan", 2000, None)  # type: ignore[arg-type]
        self.assertTrue(p.is_homeless())
