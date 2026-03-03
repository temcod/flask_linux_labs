# Тесты для test_task2_execute_endpoint.py. Проверяем работу endpoint'а и контекстных менеджеров.

import unittest

from web.app import create_app


class ExecuteEndpointTestCase(unittest.TestCase):
    

    @classmethod
    def setUpClass(cls):
        cls.app = create_app({"TESTING": True})
        cls.client = cls.app.test_client()

    def test_timeout_is_enforced(self):
       
        code = "import time\ntime.sleep(2)\nprint('done')"
        resp = self.client.post("/execute", data={"code": code, "timeout": 1})
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["timed_out"])
        self.assertIn("timeout", payload["message"].lower())

    def test_invalid_form_data_returns_errors(self):
        
        resp = self.client.post("/execute", data={"code": "print('x')", "timeout": 0})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertFalse(payload["ok"])
        self.assertIn("timeout", payload["errors"])

    def test_shell_injection_like_input_is_not_executed(self):
        
        code = 'print()"; echo "hacked"'
        resp = self.client.post("/execute", data={"code": code, "timeout": 5})
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        combined = (payload.get("stdout", "") + payload.get("stderr", "")).lower()
        self.assertNotIn("hacked", combined)
       
        self.assertIn("syntax", combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
