# Тесты для test_task4_redirect.py. Проверяем работу endpoint'а и контекстных менеджеров.

import io
import sys
import traceback
import unittest

from utils.context_managers import Redirect


class RedirectTestCase(unittest.TestCase):
    

    def test_stdout_is_redirected(self):
        
        buf = io.StringIO()
        with Redirect(stdout=buf):
            print("Hello stdout.txt")
        self.assertIn("Hello stdout.txt", buf.getvalue())

    def test_stderr_traceback_is_redirected(self):
        
        err = io.StringIO()
        with Redirect(stderr=err):
            try:
                raise ValueError("Hello stderr.txt")
            except Exception:
                sys.stderr.write(traceback.format_exc())
        self.assertIn("ValueError", err.getvalue())
        self.assertIn("Hello stderr.txt", err.getvalue())

    def test_nested_blocks_restore_previous_streams(self):
       
        outer_out = io.StringIO()
        inner_out = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        with Redirect(stdout=outer_out):
            print("outer-1")
            with Redirect(stdout=inner_out):
                print("inner")
            print("outer-2")

      
        self.assertIn("outer-1", outer_out.getvalue())
        self.assertIn("outer-2", outer_out.getvalue())
        self.assertIn("inner", inner_out.getvalue())

       
        self.assertIs(sys.stdout, original_stdout)
        self.assertIs(sys.stderr, original_stderr)

    def test_context_manager_without_args_does_not_break(self):
       
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        with Redirect():
            pass
        self.assertIs(sys.stdout, original_stdout)
        self.assertIs(sys.stderr, original_stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
