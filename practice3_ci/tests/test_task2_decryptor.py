# Тесты для test_task2_decryptor.py. Здесь проверяем задания практики 3 (unittest).

from __future__ import annotations

import unittest

from cli.task3_decrypt import decrypt


class DecryptorTests(unittest.TestCase):
    """Задача 2. Дешифратор — тесты на все проверки из условия."""

    def test_one_dot(self) -> None:
        """Случаи с одиночными точками (точка просто удаляется)."""
        cases = {
            "абра-кадабра.": "абра-кадабра",
            ".": "",
        }
        for cipher, expected in cases.items():
            with self.subTest(cipher=cipher):
                self.assertEqual(decrypt(cipher), expected)

    def test_two_dots(self) -> None:
        """Случаи, где встречается '..' (удаляется предыдущий символ)."""
        cases = {
            "абраа..-кадабра": "абра-кадабра",
            "абра--..кадабра": "абра-кадабра",
            "1..2.3": "23",
        }
        for cipher, expected in cases.items():
            with self.subTest(cipher=cipher):
                self.assertEqual(decrypt(cipher), expected)

    def test_mixed_dots(self) -> None:
        """Смешанные случаи: '..' + '.' и последовательности из 3 точек."""
        cases = {
            "абраа..-.кадабра": "абра-кадабра",
            "абрау...-кадабра": "абра-кадабра",
        }
        for cipher, expected in cases.items():
            with self.subTest(cipher=cipher):
                self.assertEqual(decrypt(cipher), expected)

    def test_many_dots(self) -> None:
        """Длинные последовательности точек."""
        cases = {
            "абра........": "",
            "абр......a.": "a",
            "1.......................": "",
        }
        for cipher, expected in cases.items():
            with self.subTest(cipher=cipher):
                self.assertEqual(decrypt(cipher), expected)
