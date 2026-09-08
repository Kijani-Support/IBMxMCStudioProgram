import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import auth_security
import settings


class AuthenticationThrottleTests(unittest.TestCase):
    def setUp(self):
        auth_security._failures.clear()

    def test_blocks_after_five_failed_attempts(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for _ in range(5):
            auth_security.record_failure("USER@example.com", now)
        self.assertTrue(auth_security.is_blocked("user@example.com", now))
        auth_security.clear_failures("user@example.com")
        self.assertFalse(auth_security.is_blocked("user@example.com", now))


class RuntimeSettingsTests(unittest.TestCase):
    def test_production_rejects_default_secret(self):
        with patch.object(settings, "ENVIRONMENT", "production"), patch.dict(
            os.environ, {"VIZIER_STORAGE_SECRET": settings.DEFAULT_STORAGE_SECRET}, clear=False
        ):
            with self.assertRaises(RuntimeError):
                settings.validate_runtime()


if __name__ == "__main__":
    unittest.main()
