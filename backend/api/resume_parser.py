"""
简历解析 API - 将上传的简历转换为结构化 JSON
"""
import json
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

try:
    from ..core.tools.ocr_processing import perform_ocr
    OCR_AVAILABLE = True
except Exception:
    perform_ocr = None
    OCR_AVAILABLE = False

from ..core.llm_client import DeepSeekClient
from ..core.prompts.resume_parser_prompt import generate_parser_prompt
from ..services.resume_text_extraction import (
    ResumeExtractionError,
    ResumeOcrUnavailableError,
    SUPPORTED_RESUME_EXTENSIONS,
    ensure_supported_resume_extension,
    extract_resume_content,
)

resume_parser_bp = Blueprint('resume_parser', __name__)

# 允许的文件类型
ALLOWED_EXTENSIONS = {ext.lstrip('.') for ext in SUPPORTED_RESUME_EXTENSIONS}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_parser_bp.route('/api/resume/parse', methods=['POST'])
def parse_resume():
    """
    解析上传的简历文件，返回结构化 JSON

    Request:
        - file: 简历文件（PDF/图片/DOCX/MD/TXT）
        - mode: 'ocr' | 'pdf' (可选，自动检测)

    Response:
        {
            "status": "success",
            "data": {
                "basicInfo": {...},
                "modules": [...]
            },
            "raw_text": "提取的原始文本（用于调试）"
        }
    """
    # 1. 检查文件
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "未上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "文件名为空"}), 400

    if not allowed_file(file.filename):
        try:
            ensure_supported_resume_extension(file.filename)
        except ResumeExtractionError as exc:
            return jsonify({"status": "error", "message": str(exc)}), 400
        return jsonify({"status": "error", "message": "不支持的文件格式"}), 400

    temp_path: Path | None = None
    try:
        # 2. 保存临时文件
        original_name = secure_filename(file.filename)
        ext = ensure_supported_resume_extension(original_name)
        temp_path = Path(tempfile.gettempdir()) / f"resume_{uuid.uuid4().hex}{ext}"
        file.save(str(temp_path))

        # 3. 提取文本
        extraction = extract_resume_content(
            str(temp_path),
            include_images=False,
            ocr_available=OCR_AVAILABLE,
            ocr_text_loader=perform_ocr if OCR_AVAILABLE else None,
        )
        if not extraction["success"]:
            return jsonify({
                "status": "error",
                "message": extraction["error_message"] or "简历内容提取失败"
            }), 400

        resume_text = extraction["text"]
        if not resume_text or len(resume_text.strip()) < 50:
            return jsonify({
                "status": "error",
                "message": "简历内容提取失败或内容过少，请确保文件清晰可读"
            }), 400

        # 4. 调用 LLM 解析
        system_prompt, user_prompt = generate_parser_prompt(resume_text)
        llm_client = DeepSeekClient()

        response = llm_client.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # 低温度保证稳定输出
            max_tokens=4000
        )

        # 5. 解析 JSON
        try:
            # 清理可能的代码块标记
            json_text = response.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.startswith('```'):
                json_text = json_text[3:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            json_text = json_text.strip()

            parsed_data = json.loads(json_text)

            # 6. 数据校验与补全
            validated_data = validate_and_complete_resume_data(parsed_data)

            return jsonify({
                "status": "success",
                "data": validated_data,
                "raw_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
            })

        except json.JSONDecodeError as e:
            return jsonify({
                "status": "error",
                "message": f"JSON 解析失败: {str(e)}",
                "raw_response": response[:500]
            }), 500

    except ResumeOcrUnavailableError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 503
    except ResumeExtractionError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"解析失败: {str(e)}"
        }), 500
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


def validate_and_complete_resume_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    校验并补全简历数据，确保符合前端 Schema

    1. 为每个模块生成唯一 ID
    2. 补全缺失的必需字段
    3. 设置默认的 sortIndex
    """
    # 补全 basicInfo
    if 'basicInfo' not in data:
        data['basicInfo'] = {}

    basic_defaults = {
        'name': '', 'gender': '', 'birthday': '', 'email': '',
        'mobile': '', 'location': '', 'workYears': '', 'photoUrl': ''
    }
    for key, default in basic_defaults.items():
        if key not in data['basicInfo']:
            data['basicInfo'][key] = default

    # 处理 modules
    if 'modules' not in data or not isinstance(data['modules'], list):
        data['modules'] = []

    for idx, module in enumerate(data['modules']):
        # 生成 ID
        if 'id' not in module:
            module['id'] = f"mod_{uuid.uuid4().hex[:12]}"

        # 补全必需字段
        if 'visible' not in module:
            module['visible'] = True
        if 'sortIndex' not in module:
            module['sortIndex'] = idx

        # 为 entries 生成 ID
        if 'entries' in module and isinstance(module['entries'], list):
            for entry in module['entries']:
                if 'id' not in entry:
                    entry['id'] = f"ent_{uuid.uuid4().hex[:12]}"

    return data
