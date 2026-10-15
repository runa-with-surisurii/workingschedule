import unittest
from fastapi import HTTPException

from backend.main import hours, pw_hash, pw_ok


class BusinessRuleTests(unittest.TestCase):
    def test_hours_calculates_duration(self):
        self.assertEqual(hours("08:00", "16:30"), 8.5)

    def test_hours_rejects_invalid_format(self):
        with self.assertRaises(HTTPException):
            hours("8am", "16:00")

    def test_hours_rejects_end_before_start(self):
        with self.assertRaises(HTTPException):
            hours("17:00", "09:00")

    def test_password_hash_verifies_correct_password(self):
        stored = pw_hash("ExamplePass123!")
        self.assertTrue(pw_ok("ExamplePass123!", stored))

    def test_password_hash_rejects_wrong_password(self):
        stored = pw_hash("ExamplePass123!")
        self.assertFalse(pw_ok("wrong-password", stored))


if __name__ == "__main__":
    unittest.main()
