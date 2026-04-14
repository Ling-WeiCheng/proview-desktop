import os
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module
from direct_store import DirectDataStore


class HistoryRetentionApiTests(unittest.TestCase):
    def setUp(self):
        self.original_storage_available = app_module.STORAGE_AVAILABLE
        self.original_data_client = app_module.data_client
        self.client = app_module.app.test_client()

    def tearDown(self):
        app_module.STORAGE_AVAILABLE = self.original_storage_available
        app_module.data_client = self.original_data_client

    def test_history_quota_is_unlimited(self):
        data_client = MagicMock()
        data_client.count_user_sessions.return_value = 23

        app_module.STORAGE_AVAILABLE = True
        app_module.data_client = data_client

        with patch.object(app_module, "_get_current_user_id_from_auth_header", return_value=1):
            response = self.client.get("/api/history/quota")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "saved_count": 23,
                "max_saved": None,
                "remaining": None,
                "can_save": True,
            },
        )

    def test_history_sessions_endpoint_requests_all_records(self):
        sessions = [
            {
                "session_id": f"session-{index}",
                "status": "completed",
                "position": "前端工程师",
                "candidate_name": "本地用户",
                "interview_style": "strict",
                "start_time": f"2026-01-{(index % 28) + 1:02d}T10:00:00",
                "end_time": f"2026-01-{(index % 28) + 1:02d}T10:30:00",
                "metadata": {},
            }
            for index in range(60)
        ]
        data_client = MagicMock()
        data_client.list_sessions = MagicMock(return_value=sessions)

        app_module.STORAGE_AVAILABLE = True
        app_module.data_client = data_client

        with patch.object(app_module, "_get_current_user_info", return_value={"id": 1, "username": "local"}):
            response = self.client.get("/api/history/sessions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 60)
        data_client.list_sessions.assert_called_once_with(limit=None, user_id=1)

    def test_my_resumes_endpoint_only_reads_existing_records(self):
        data_client = MagicMock()
        data_client.list_user_resumes.return_value = [
            {
                "id": 1,
                "session_id": "session-1",
                "file_name": "resume-1.txt",
                "file_path": "D:/tmp/resume-1.txt",
                "upload_time": "2026-01-01T10:00:00",
            }
        ]

        app_module.STORAGE_AVAILABLE = True
        app_module.data_client = data_client

        with patch.object(app_module, "_get_current_user_id_from_auth_header", return_value=1):
            response = self.client.get("/api/my-resumes")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)
        data_client.list_user_resumes.assert_called_once_with(1)


class ResumeRetentionStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(__file__).resolve().parent / ".codex_tmp_history_retention"
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir = self.temp_dir / "uploads"
        self.db_path = self.temp_dir / "resumes.sqlite3"
        self.store = DirectDataStore(
            db_url=f"sqlite:///{self.db_path.as_posix()}",
            upload_dir=str(self.upload_dir),
            secret_key="test-secret",
        )
        self.user = self.store.get_or_create_local_user("本地用户")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_resume_keeps_more_than_five_records(self):
        user_id = self.user["id"]

        for index in range(6):
            session_id = f"session-{index}"
            self.store.create_session(
                session_id=session_id,
                candidate_name="本地用户",
                position="后端工程师",
                interview_style="strict",
                metadata={},
                user_id=user_id,
            )

            file_path = self.upload_dir / f"resume-{index}.txt"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f"resume-{index}", encoding="utf-8")

            saved = self.store.save_resume(
                session_id=session_id,
                file_name=file_path.name,
                file_path=str(file_path),
                ocr_result=f"ocr-result-{index}",
                user_id=user_id,
            )
            self.assertTrue(saved)

        resumes = self.store.list_user_resumes(user_id)

        self.assertEqual(len(resumes), 6)


if __name__ == "__main__":
    unittest.main()
