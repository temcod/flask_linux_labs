# Юнит-тесты для test_registration.py. Проверяем валидаторы и endpoints через test_client.

import unittest
from web.app import create_app


class RegistrationValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(testing=True)
        cls.client = cls.app.test_client()

    def _valid_payload(self):
        return {
            "email": "user@example.com",
            "phone": 1234567890,
            "name": "Ivan",
            "address": "Lenina 1",
            "index": 620000,
            "comment": "optional",
        }

    def test_email_valid_passes(self):
        payload = self._valid_payload()
        payload["email"] = "a.b-c+tag@sub.example.org"
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_email_invalid_format_fails(self):
        payload = self._valid_payload()
        payload["email"] = "not-an-email"
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertTrue(any("email:" in e for e in data["errors"]))

    def test_email_missing_fails(self):
        payload = self._valid_payload()
        payload.pop("email")
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_phone_valid_10_digits_passes(self):
        payload = self._valid_payload()
        payload["phone"] = 9998887766
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_phone_wrong_length_fails(self):
        payload = self._valid_payload()
        payload["phone"] = 12345
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertTrue(any("phone:" in e for e in data["errors"]))

    def test_phone_negative_fails(self):
        payload = self._valid_payload()
        payload["phone"] = -1234567890
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_phone_non_number_fails_idiot_proof(self):
        payload = self._valid_payload()
        payload["phone"] = "abc"
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
      
        self.assertTrue("phone" in data["field_errors"])

    def test_name_required_fails(self):
        payload = self._valid_payload()
        payload["name"] = ""
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_name_valid_passes(self):
        payload = self._valid_payload()
        payload["name"] = "Petr"
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_address_required_fails(self):
        payload = self._valid_payload()
        payload.pop("address")
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_address_valid_passes(self):
        payload = self._valid_payload()
        payload["address"] = "New address"
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_index_required_fails(self):
        payload = self._valid_payload()
        payload.pop("index")
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)

    def test_index_non_number_fails_idiot_proof(self):
        payload = self._valid_payload()
        payload["index"] = "qwerty"
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertTrue("index" in data["field_errors"])

    def test_index_valid_passes(self):
        payload = self._valid_payload()
        payload["index"] = 123456
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_comment_optional_missing_passes(self):
        payload = self._valid_payload()
        payload.pop("comment")
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_response_contains_errors_list_on_invalid(self):
        payload = self._valid_payload()
        payload["email"] = "bad"
        r = self.client.post("/registration", json=payload)
        self.assertEqual(r.status_code, 400)
        data = r.get_json()
        self.assertIn("errors", data)
        self.assertIsInstance(data["errors"], list)


if __name__ == "__main__":
    unittest.main()
