# Тесты для test_task3_block_errors.py. Проверяем работу endpoint'а и контекстных менеджеров.

import unittest

from utils.context_managers import BlockErrors


class BlockErrorsTestCase(unittest.TestCase):
    

    def test_error_is_ignored(self):
       
        err_types = {ZeroDivisionError, TypeError}
        with BlockErrors(err_types):
            _ = 1 / 0

    def test_unexpected_error_is_raised(self):
       
        err_types = {ZeroDivisionError}
        with self.assertRaises(TypeError):
            with BlockErrors(err_types):
                _ = 1 / "0"

    def test_inner_raised_outer_ignored(self):
        
        outer_err_types = {TypeError}
        with BlockErrors(outer_err_types):
            inner_err_types = {ZeroDivisionError}
            with self.assertRaises(TypeError):
                with BlockErrors(inner_err_types):
                    _ = 1 / "0"

    def test_child_exceptions_are_ignored(self):
      
        err_types = {Exception}
        with BlockErrors(err_types):
            _ = 1 / "0"


if __name__ == "__main__":
    unittest.main(verbosity=2)
