import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from core.prompt_manager import PromptManager


class PromptManagerJobRequirementsTests(unittest.TestCase):
    def test_generate_system_prompt_includes_job_requirements_as_benchmark(self):
        manager = PromptManager()

        prompt = manager.generate_system_prompt(
            job_title="高级前端开发工程师",
            interview_type="technical",
            difficulty="mid",
            style="strict",
            feature_vad=True,
            feature_deep=True,
            resume_summary="候选人有 React 和工程化经验。",
            job_requirements="需要熟悉 React、TypeScript、性能优化，有低代码平台经验优先。",
        )

        self.assertIn("## 岗位要求（考察基准，不代表候选人已具备）", prompt)
        self.assertIn("需要熟悉 React、TypeScript、性能优化", prompt)
        self.assertIn("只能作为你设置提问重点、追问方向和评分标准的依据", prompt)
        self.assertIn("严禁把岗位要求误当成候选人已经具备的真实经历", prompt)
        self.assertIn("候选人真实简历内容", prompt)

    def test_generate_system_prompt_omits_job_requirements_section_when_empty(self):
        manager = PromptManager()

        prompt = manager.generate_system_prompt(
            job_title="高级前端开发工程师",
            interview_type="technical",
            difficulty="mid",
            style="strict",
            feature_vad=True,
            feature_deep=True,
            resume_summary="候选人有 React 和工程化经验。",
            job_requirements="",
        )

        self.assertNotIn("## 岗位要求（考察基准，不代表候选人已具备）", prompt)


if __name__ == "__main__":
    unittest.main()
