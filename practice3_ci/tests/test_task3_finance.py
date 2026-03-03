# Тесты для test_task3_finance.py. Здесь проверяем задания практики 3 (unittest).

from __future__ import annotations

import unittest

from web.app import app, storage


class FinanceBaseTestCase(unittest.TestCase):
    """База для тестов финансового приложения (Задача 3)."""

    @classmethod
    def setUpClass(cls) -> None:
        app.config.update(TESTING=True)

        # Общие данные для всех тестов (рекомендация из задания).
        cls.seed_data = [
            ("20260101", 100),
            ("20260214", 150),
            ("20260215", 50),
            ("20251231", 10),
        ]

    def setUp(self) -> None:
        # Перед каждым тестом приводим storage к одной и той же базе.
        storage.clear()
        for date, amount in self.seed_data:
            storage.add(date, amount)

        self.client = app.test_client()


class AddEndpointTests(FinanceBaseTestCase):
    """Тесты endpoint /add/ (не менее 3-х)."""

    def test_add_increases_daily_total(self) -> None:
        resp = self.client.get("/add/20260214/25")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Итого за день: 175", resp.get_data(as_text=True))

    def test_add_new_day_creates_record(self) -> None:
        resp = self.client.get("/add/20260301/10")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Итого за день: 10", resp.get_data(as_text=True))
        self.assertEqual(storage.daily.get("20260301"), 10)

    def test_add_invalid_date_raises(self) -> None:
        # Дата НЕ в формате YYYYMMDD => datetime.strptime бросает ValueError,
        # в TESTING=True исключение пробрасывается в тест.
        with self.assertRaises(ValueError):
            self.client.get("/add/2026-02-14/10")


class CalculateYearEndpointTests(FinanceBaseTestCase):
    """Тесты endpoint /calculate/<year>."""

    def test_calculate_year_returns_sum(self) -> None:
        resp = self.client.get("/calculate/2026")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("300", resp.get_data(as_text=True))

    def test_calculate_year_missing_returns_zero(self) -> None:
        resp = self.client.get("/calculate/1999")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("0", resp.get_data(as_text=True))

    def test_calculate_year_updates_after_add(self) -> None:
        self.client.get("/add/20260216/20")
        resp = self.client.get("/calculate/2026")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("320", resp.get_data(as_text=True))

    def test_calculate_year_empty_storage(self) -> None:
        storage.clear()
        resp = self.client.get("/calculate/2026")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("0", resp.get_data(as_text=True))


class CalculateMonthEndpointTests(FinanceBaseTestCase):
    """Тесты endpoint /calculate/<year>/<month>."""

    def test_calculate_month_returns_sum(self) -> None:
        resp = self.client.get("/calculate/2026/2")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("200", resp.get_data(as_text=True))

    def test_calculate_month_missing_returns_zero(self) -> None:
        resp = self.client.get("/calculate/2026/3")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("0", resp.get_data(as_text=True))

    def test_calculate_month_invalid_month_returns_400(self) -> None:
        resp = self.client.get("/calculate/2026/13")
        self.assertEqual(resp.status_code, 400)

    def test_calculate_month_empty_storage(self) -> None:
        storage.clear()
        resp = self.client.get("/calculate/2026/2")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("0", resp.get_data(as_text=True))
