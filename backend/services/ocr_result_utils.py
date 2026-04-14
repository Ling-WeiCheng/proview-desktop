from __future__ import annotations


SUCCESS_MARKERS = (
    "解析成功",
    "【解析成功】",
    "以下是提取的内容",
)

INVALID_MARKERS = (
    "[error]",
    "[unavailable]",
    "[not_called]",
    "error:",
    "ocr api",
    "ocr 调用异常",
    "api 令牌未配置",
    "无法连接到ocr",
    "错误:",
)


def is_reusable_ocr_result(value: object) -> bool:
    text = str(value or "").strip()
    if not text:
        return False

    lowered = text.lower()
    if any(marker in lowered for marker in INVALID_MARKERS):
        return False

    if any(marker in text for marker in SUCCESS_MARKERS):
        return True

    return len(text) >= 200


def normalize_reusable_ocr_result(value: object) -> str:
    text = str(value or "").strip()
    return text if is_reusable_ocr_result(text) else ""
