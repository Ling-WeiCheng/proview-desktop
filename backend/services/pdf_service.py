"""Playwright PDF 渲染服务"""
import os
import uuid
import asyncio
from playwright.async_api import async_playwright
from runtime_paths import get_app_data_path, get_resource_path

TEMPLATE_DIR = str(get_resource_path('templates'))
OUTPUT_DIR = str(get_app_data_path('temp', 'generated', is_dir=True))

os.makedirs(OUTPUT_DIR, exist_ok=True)


async def _render_pdf(html_content: str, output_path: str) -> None:
    """用 Playwright 将 HTML 渲染为 A4 PDF（每次独立启动浏览器，避免跨事件循环状态污染）"""
    async with async_playwright() as pw:
        launch_options = {"headless": True}
        browser_channel = os.getenv("PROVIEW_PLAYWRIGHT_CHANNEL", "").strip()
        if browser_channel:
            launch_options["channel"] = browser_channel
        browser = await pw.chromium.launch(**launch_options)
        try:
            page = await browser.new_page()
            # 设置视口为 A4 宽度（794px = 210mm @ 96dpi），防止内容被缩放
            await page.set_viewport_size({"width": 794, "height": 1123})
            await page.set_content(html_content, wait_until='networkidle')
            await page.pdf(
                path=output_path,
                format='A4',
                margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'},
                print_background=True,
                scale=1,
            )
        finally:
            await browser.close()


def render_html_to_pdf(html_content: str) -> str:
    """同步入口：HTML → PDF，返回生成的文件路径"""
    filename = f"{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    try:
        asyncio.run(_render_pdf(html_content, output_path))
    except RuntimeError as e:
        # 如果已有运行中的事件循环（如 Jupyter），在新线程中运行
        if "cannot be called from a running event loop" in str(e):
            import threading
            exc_holder = [None]
            def run_in_thread():
                try:
                    asyncio.run(_render_pdf(html_content, output_path))
                except Exception as ex:
                    exc_holder[0] = ex
            t = threading.Thread(target=run_in_thread)
            t.start()
            t.join()
            if exc_holder[0]:
                raise exc_holder[0]
        else:
            raise

    return output_path


def render_resume_pdf(html_body: str) -> str:
    """完整流程：用 Jinja2 模板包裹 HTML body，再渲染 PDF"""
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('resume_template.html')
    full_html = template.render(content=html_body)
    return render_html_to_pdf(full_html)
