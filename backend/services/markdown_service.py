"""Markdown → HTML 转换服务"""
import re
import markdown


def convert_markdown_to_html(md_text: str) -> str:
    """将 Markdown 文本转换为 HTML，支持表格、代码块、目录等扩展"""
    extensions = [
        'tables',
        'fenced_code',
        'toc',
        'nl2br',        # 换行符转 <br>
        'sane_lists',   # 更合理的列表解析
    ]
    return markdown.markdown(md_text, extensions=extensions)


def _strip_embedded_images(text: str) -> str:
    """剥离 OCR 嵌入的 <div><img></div> 图片块"""
    return re.sub(r'<div[^>]*>\s*<img[^>]*/?>\s*</div>', '', text, flags=re.IGNORECASE)


def _render_section_content(content: str) -> str:
    """将 section 的 markdown content 转为 HTML，剥离嵌入图片"""
    cleaned = _strip_embedded_images(content)
    extensions = ['tables', 'fenced_code', 'sane_lists']
    return markdown.markdown(cleaned, extensions=extensions)


def sections_to_html(sections: list) -> str:
    """将结构化 sections 列表转为完整的简历 HTML（用于 PDF 导出）

    每个 section 包裹在 .resume-section 中，配合 CSS break 规则防止
    标题孤立在页底、内容断层等分页问题。
    """
    parts = []

    for sec in sections:
        sec_type = sec.get('type', 'other')
        title = sec.get('title', '')
        content = sec.get('content', '')

        if sec_type == 'personal_info':
            # 个人信息：整块不跨页
            content_html = _render_section_content(content)
            parts.append(
                f'<div class="personal-info-block">'
                f'<h1>{_esc(title)}</h1>'
                f'<div class="personal-info">{content_html}</div>'
                f'</div>'
            )
        else:
            # 其他 section：h2 + 内容包裹在 .resume-section 中
            content_html = _render_section_content(content)
            parts.append(
                f'<div class="resume-section">'
                f'<h2>{_esc(title)}</h2>'
                f'<div class="section-body">{content_html}</div>'
                f'</div>'
            )

    return '\n'.join(parts)


def _esc(text: str) -> str:
    """HTML 转义"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))
