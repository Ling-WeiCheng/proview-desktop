import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from pydantic.v1 import BaseModel as PydanticV1BaseModel
    from core.langchain_agent import LangChainInterviewAgent
    from core.tools.langchain_tools import GoogleSearchInput, OCRInput, create_langchain_tools
    LANGCHAIN_DEPS_AVAILABLE = True
except ImportError:
    PydanticV1BaseModel = None
    LangChainInterviewAgent = None
    GoogleSearchInput = None
    OCRInput = None
    create_langchain_tools = None
    LANGCHAIN_DEPS_AVAILABLE = False


@unittest.skipUnless(LANGCHAIN_DEPS_AVAILABLE, "langchain/pydantic dependencies are not installed")
class LangChainToolsCompatibilityTests(unittest.TestCase):
    def test_tool_input_models_use_pydantic_v1_namespace(self):
        self.assertTrue(issubclass(GoogleSearchInput, PydanticV1BaseModel))
        self.assertTrue(issubclass(OCRInput, PydanticV1BaseModel))

    def test_create_langchain_tools_registers_structured_tools(self):
        tools = create_langchain_tools()

        self.assertEqual([tool.name for tool in tools], ["google_search", "perform_ocr"])
        self.assertIs(tools[0].args_schema, GoogleSearchInput)
        self.assertIs(tools[1].args_schema, OCRInput)

    def test_agent_falls_back_when_tool_registry_init_fails(self):
        with patch("core.langchain_agent.LangChainToolRegistry", side_effect=RuntimeError("boom")), \
             patch("core.langchain_agent.HAVE_LANGCHAIN", False), \
             patch("core.langchain_agent.traceback.print_exc"):
            agent = LangChainInterviewAgent(
                llm_client=None,
                verbose=False,
            )

        self.assertEqual(agent.tools, [])
        self.assertEqual(
            agent.tool_registry.execute_tool("google_search"),
            "错误：工具 google_search 暂时不可用。",
        )


if __name__ == "__main__":
    unittest.main()
