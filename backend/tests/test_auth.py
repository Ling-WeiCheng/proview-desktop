import os
import shutil
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import auth


class AuthStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(__file__).resolve().parent / ".codex_tmp_auth"
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.original_db_path = auth._TOKEN_DB_PATH
        auth._TOKEN_DB_PATH = self.temp_dir / "session_tokens.sqlite3"

    def tearDown(self):
        auth._TOKEN_DB_PATH = self.original_db_path
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _list_tables(self):
        conn = sqlite3.connect(auth._TOKEN_DB_PATH)
        try:
            return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            conn.close()

    def test_create_token_initializes_schema_for_new_database(self):
        token = auth.create_token("session-1")

        self.assertTrue(token)
        self.assertEqual(auth.get_session_id(token), "session-1")
        self.assertIn("interview_tokens", self._list_tables())

    def test_create_token_recovers_from_preexisting_empty_sqlite_file(self):
        auth._TOKEN_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        auth._TOKEN_DB_PATH.touch()

        token = auth.create_token("session-2")

        self.assertTrue(token)
        self.assertEqual(auth.get_session_id(token), "session-2")
        self.assertIn("interview_tokens", self._list_tables())


if __name__ == "__main__":
    unittest.main()
