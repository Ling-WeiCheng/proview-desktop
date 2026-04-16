import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module


class AppRuntimeTests(unittest.TestCase):
    def test_debug_mode_defaults_to_false_for_desktop(self):
        with patch.dict(os.environ, {"PROVIEW_DESKTOP_MODE": "1"}, clear=False):
            with patch.dict(os.environ, {"PROVIEW_DEBUG": "", "FLASK_DEBUG": ""}, clear=False):
                self.assertFalse(app_module._should_enable_debug_mode())

    def test_debug_mode_can_be_explicitly_enabled(self):
        with patch.dict(
            os.environ,
            {"PROVIEW_DESKTOP_MODE": "1", "PROVIEW_DEBUG": "1"},
            clear=False,
        ):
            self.assertTrue(app_module._should_enable_debug_mode())


class ApiErrorHandlingTests(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()

    def test_missing_api_route_returns_json(self):
        response = self.client.get("/api/route-that-does-not-exist")
        payload = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertEqual(payload["status"], "error")

    def test_unhandled_api_exception_returns_json(self):
        with patch.object(app_module, "_refresh_storage_status", side_effect=RuntimeError("boom")):
            response = self.client.get("/api/health")

        payload = response.get_json()
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.content_type.startswith("application/json"))
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["message"], "服务器内部错误，请稍后重试。")


if __name__ == "__main__":
    unittest.main()
