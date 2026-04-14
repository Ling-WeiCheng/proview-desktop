import axios from 'axios'
import { buildApiUrl } from '../services/runtimeConfig'

export interface ExportOptions {
  filename?: string
  format?: 'pdf' | 'png'
  quality?: number
}

/**
 * 简历导出 Hook — 使用后端 Playwright 实现服务端导出
 *
 * 优势：
 * 1. 完美支持所有 CSS 特性（包括 oklch 等现代颜色函数）
 * 2. 无需处理 CORS 和跨域图片
 * 3. 渲染质量更高，字体更清晰
 * 4. 避免客户端性能问题
 */
export function useResumeExport() {
  async function exportResume(
    element: HTMLElement,
    options: ExportOptions = {}
  ): Promise<void> {
    const {
      filename = `简历_${Date.now()}`,
      format = 'pdf',
    } = options

    if (format !== 'pdf') {
      throw new Error('目前仅支持 PDF 格式导出')
    }

    try {
      // 1. 获取元素的完整 HTML（包括内联样式）
      const clonedElement = element.cloneNode(true) as HTMLElement

      // 2. 收集所有样式表
      const styles = Array.from(document.styleSheets)
        .map(sheet => {
          try {
            return Array.from(sheet.cssRules)
              .map(rule => rule.cssText)
              .join('\n')
          } catch (e) {
            // 跨域样式表无法访问，跳过
            return ''
          }
        })
        .join('\n')

      // 3. 构建完整的 HTML 文档
      const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    ${styles}
    body { margin: 0; padding: 0; }
  </style>
</head>
<body>
  ${clonedElement.outerHTML}
</body>
</html>
`

      // 4. 调用后端 API
      const response = await axios.post(buildApiUrl('/api/export-html-pdf'),
        { html: fullHtml },
        { responseType: 'blob', timeout: 60000 }
      )

      // 5. 触发下载
      const blob = response.data
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.pdf`
      a.click()
      URL.revokeObjectURL(url)

    } catch (error: any) {
      console.error('导出失败:', error)
      const errorMessage = error?.response?.data?.message || error?.message || String(error)
      throw new Error(`导出失败: ${errorMessage}`)
    }
  }

  return {
    exportResume,
  }
}
