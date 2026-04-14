import os
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app as app_module
from services.career_planning_docs import CareerPlanningDocumentRepository
from services.career_planning_service import CareerPlanningService


def make_workspace_tempdir(name: str) -> Path:
    path = Path(__file__).resolve().parent / name
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    return path


class MockDataClient:
    def __init__(self):
        self.get_user = MagicMock(return_value={"id": 1})
        self.get_or_create_local_user = MagicMock(return_value={"id": 1, "username": "本地用户", "display_name": "本地用户"})
        self.get_latest_resume = MagicMock(return_value={"file_name": "resume.pdf", "title": "后端工程师简历"})
        self.list_sessions = MagicMock(return_value=[
            {
                "session_id": "session-1",
                "status": "completed",
                "position": "高级前端开发工程师",
            }
        ])
        self.get_session_statistics = MagicMock(return_value={
            "turn_count": 4,
            "evaluations": [
                {"dimension": "表达", "score": 8, "comment": "good"},
                {"dimension": "系统设计", "score": 6, "comment": "gap"},
            ],
            "avg_score": 7.0,
        })


class EmptyContextDataClient(MockDataClient):
    def __init__(self):
        super().__init__()
        self.get_latest_resume = MagicMock(return_value=None)
        self.list_sessions = MagicMock(return_value=[])
        self.get_session_statistics = MagicMock(return_value={
            "turn_count": 0,
            "evaluations": [],
            "avg_score": 0,
        })


class CareerPlanningServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = make_workspace_tempdir(".codex_tmp_career_planning_service")
        self.data_client = MockDataClient()
        self.service = CareerPlanningService(self.data_client, db_path=str(self.temp_dir / "career.sqlite3"))

    def tearDown(self):
        self.service = None
        self.data_client = None
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_plan_creates_persistent_dashboard(self):
        result = self.service.generate_plan(
            user_id=1,
            target_role="高级前端开发工程师",
            career_goal="6 个月内拿到 offer",
            horizon_months=6,
            refresh=True,
        )

        self.assertEqual(result["profile"]["user_id"], 1)
        self.assertGreaterEqual(len(result["plans"]), 1)
        self.assertGreaterEqual(len(result["milestones"]), 1)
        self.assertGreaterEqual(len(result["tasks"]), 1)

        dashboard = self.service.build_dashboard(1)
        self.assertEqual(dashboard["stats"]["plan_count"], len(dashboard["plans"]))
        self.assertGreaterEqual(dashboard["stats"]["progress_rate"], 0)

    def test_update_task_rejects_unknown_task(self):
        self.assertIsNone(self.service.update_task(1, 999999, status="completed"))

    def test_horizon_months_are_clamped(self):
        result = self.service.generate_plan(user_id=1, horizon_months=99)
        self.assertLessEqual(result["current_plan"]["horizon_months"], 12)

    def test_generate_plan_reuses_active_plan_without_refresh(self):
        first = self.service.generate_plan(
            user_id=1,
            target_role="高级前端开发工程师",
            career_goal="6 个月内拿到 offer",
            horizon_months=6,
            refresh=True,
        )

        second = self.service.generate_plan(user_id=1)

        self.assertEqual(len(second["plans"]), 1)
        self.assertEqual(first["current_plan"]["id"], second["current_plan"]["id"])

    def test_build_dashboard_returns_empty_state_when_target_role_missing(self):
        empty_service = CareerPlanningService(
            EmptyContextDataClient(),
            db_path=str(self.temp_dir / "career-empty.sqlite3"),
        )

        dashboard = empty_service.build_dashboard(1)

        self.assertEqual(dashboard["plans"], [])
        self.assertEqual(dashboard["tasks"], [])
        self.assertEqual(dashboard["stats"]["progress_rate"], 0)


class CareerPlanningDocsRepositoryTests(unittest.TestCase):
    def test_loads_structured_documents(self):
        repository = CareerPlanningDocumentRepository()
        catalog = repository.get_catalog()

        self.assertIn("documents", catalog)
        self.assertEqual(len(catalog["documents"]), 3)
        self.assertIsNotNone(repository.get_document("job-seeking-guide"))
        self.assertIsNone(repository.get_document("missing"))


class CareerPlanningApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = make_workspace_tempdir(".codex_tmp_career_planning_api")
        self.data_client = MockDataClient()
        self.service = CareerPlanningService(self.data_client, db_path=str(self.temp_dir / "career.sqlite3"))

        app_module.STORAGE_AVAILABLE = True
        app_module.data_client = self.data_client
        app_module.career_planning_service = self.service
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.client = None
        self.service = None
        self.data_client = None
        app_module.career_planning_service = None
        app_module.data_client = None
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _auth_headers(self):
        return {"Authorization": "Bearer session-token"}

    def test_docs_endpoint_uses_local_user_by_default(self):
        response = self.client.get('/api/career/docs')
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")

    def test_docs_endpoint_returns_catalog(self):
        response = self.client.get('/api/career/docs', headers=self._auth_headers())
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(len(payload["data"]["documents"]), 3)

    def test_doc_detail_endpoint_returns_specific_document(self):
        response = self.client.get('/api/career/docs/job-seeking-guide', headers=self._auth_headers())
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["data"]["id"], "job-seeking-guide")
        self.assertTrue(payload["data"]["sections"])

    def test_dashboard_endpoint_returns_generated_data(self):
        response = self.client.get('/api/career/dashboard', headers=self._auth_headers())
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertIn("profile", payload["data"])
        self.assertIn("plans", payload["data"])

    def test_dashboard_endpoint_returns_empty_state_without_target_role(self):
        empty_data_client = EmptyContextDataClient()
        empty_service = CareerPlanningService(
            empty_data_client,
            db_path=str(self.temp_dir / "career-empty-api.sqlite3"),
        )
        app_module.data_client = empty_data_client
        app_module.career_planning_service = empty_service

        response = self.client.get('/api/career/dashboard', headers=self._auth_headers())
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["data"]["plans"], [])
        self.assertEqual(payload["data"]["tasks"], [])

    def test_generate_plan_endpoint_creates_plan(self):
        response = self.client.post(
            '/api/career/plans/generate',
            headers=self._auth_headers(),
            json={"target_role": "高级前端开发工程师", "career_goal": "6 个月内拿到 offer", "horizon_months": 6, "refresh": True},
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertGreaterEqual(len(payload["data"]["plans"]), 1)

    def test_generate_plan_endpoint_rejects_invalid_horizon_months(self):
        response = self.client.post(
            '/api/career/plans/generate',
            headers=self._auth_headers(),
            json={"target_role": "高级前端开发工程师", "career_goal": "6 个月内拿到 offer", "horizon_months": "invalid"},
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["status"], "error")

    def test_task_update_roundtrip_reflects_dashboard_state(self):
        generated = self.client.post(
            '/api/career/plans/generate',
            headers=self._auth_headers(),
            json={"target_role": "高级前端开发工程师", "career_goal": "6 个月内拿到 offer", "horizon_months": 6, "refresh": True},
        ).get_json()
        task_id = generated["data"]["tasks"][0]["id"]

        update_response = self.client.patch(
            f'/api/career/tasks/{task_id}',
            headers=self._auth_headers(),
            json={"status": "completed", "progress": 100, "note": "done"},
        )
        update_payload = update_response.get_json()

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_payload["status"], "success")
        self.assertEqual(update_payload["data"]["tasks"][0]["status"], "completed")
        self.assertGreaterEqual(update_payload["data"]["stats"]["completed_task_count"], 1)

    def test_task_update_requires_existing_task(self):
        response = self.client.patch(
            '/api/career/tasks/999999',
            headers=self._auth_headers(),
            json={"status": "completed", "progress": 100, "note": "done"},
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(payload["status"], "error")

    def test_task_update_uses_local_user_by_default(self):
        response = self.client.patch('/api/career/tasks/1', json={"status": "completed"})
        payload = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(payload["status"], "error")


if __name__ == "__main__":
    unittest.main()
