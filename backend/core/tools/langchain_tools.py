"""
LangChain 工具定义模块
将现有的工具函数转换为 LangChain Tool 格式
"""
from langchain_core.tools import StructuredTool
try:
    # LangChain 0.1.x still validates args_schema against the Pydantic v1 BaseModel
    # namespace, even when the runtime uses Pydantic 2.x.
    from pydantic.v1 import BaseModel, Field
except ImportError:  # pragma: no cover - compatibility for older Pydantic installs
    from pydantic import BaseModel, Field
from typing import Optional
import os
import sys

# 导入原有的工具函数
sys.path.append(os.path.dirname(__file__))
try:
    from core.tools.google_search import google_search
    from core.tools.ocr_processing import perform_ocr
except Exception:
    try:
        from .google_search import google_search
        from .ocr_processing import perform_ocr
    except Exception:
        from google_search import google_search
        from ocr_processing import perform_ocr


# ==========================================
# Pydantic 模型定义（用于结构化输入）
# ==========================================

class GoogleSearchInput(BaseModel):
    """谷歌搜索工具的输入参数"""
    search_query: str = Field(description="搜索关键词或短语")


class OCRInput(BaseModel):
    """OCR 工具的输入参数"""
    image_path: str = Field(description="需要识别的本地图片或 PDF 文件的完整路径")
    use_preprocessing: Optional[bool] = Field(
        default=True,
        description="是否对图片进行预处理增强（倾斜校正、增强等），提升识别准确率"
    )
    is_screen_capture: Optional[bool] = Field(
        default=False,
        description="原图是否为屏幕翻拍照片（开启后会特殊去除摩尔纹）"
    )


# ==========================================
# LangChain Tool 包装器
# ==========================================

def create_langchain_tools():
    """创建并返回所有 LangChain 工具列表"""

    # 1. 谷歌搜索工具
    google_search_tool = StructuredTool.from_function(
        func=google_search,
        name="google_search",
        description="谷歌搜索是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻、查找技术文档等。适用于需要获取最新信息或验证知识点的场景。",
        args_schema=GoogleSearchInput,
        return_direct=False
    )

    # 2. OCR 文档解析工具
    ocr_tool = StructuredTool.from_function(
        func=perform_ocr,
        name="perform_ocr",
        description="光学字符识别(OCR)工具，可以提取图片或PDF中的文字、表格、排版布局信息，并转换为结构化的Markdown格式文本返回。适用于解析简历、文档、截图等场景，帮助理解本地文档内容。",
        args_schema=OCRInput,
        return_direct=False
    )

    return [google_search_tool, ocr_tool]


# ==========================================
# 工具注册表（兼容旧代码）
# ==========================================

class LangChainToolRegistry:
    """
    工具注册表，提供与旧版 ReactTools 兼容的接口
    同时支持 LangChain 的工具格式
    """

    def __init__(self):
        self.langchain_tools = create_langchain_tools()

        # 创建工具映射字典（兼容旧代码）
        self._tools_map = {
            "google_search": google_search,
            "perform_ocr": perform_ocr,
        }

    def get_langchain_tools(self):
        """返回 LangChain 格式的工具列表"""
        return self.langchain_tools

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """统一的工具执行入口（兼容旧代码）"""
        if tool_name not in self._tools_map:
            return f"错误：工具 {tool_name} 未定义。"
        return self._tools_map[tool_name](**kwargs)


if __name__ == "__main__":
    # 测试工具创建
    registry = LangChainToolRegistry()
    tools = registry.get_langchain_tools()

    print("已注册的 LangChain 工具：")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
