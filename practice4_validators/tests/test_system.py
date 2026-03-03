# Юнит-тесты для test_system.py. Проверяем валидаторы и endpoints через test_client.

\
import re
import unittest
from web.app import create_app


class SystemEndpointsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(testing=True)
        cls.client = cls.app.test_client()

    def test_uptime_returns_pretty_time(self):
        r = self.client.get("/uptime")
        self.assertEqual(r.status_code, 200)
        text = r.get_data(as_text=True)
        self.assertTrue(text.startswith("Current uptime is "))
       
        self.assertNotIn("load average", text)

    def test_ps_accepts_args_as_list(self):
        r = self.client.get("/ps?arg=a&arg=u&arg=x")
        self.assertEqual(r.status_code, 200)
        text = r.get_data(as_text=True)
        self.assertTrue(text.startswith("<pre>") and text.endswith("</pre>"))

    def test_ps_idiot_proof_injection_like_arg_does_not_crash(self):
      
        r = self.client.get("/ps?arg=aux;rm%20-rf%20/")
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
