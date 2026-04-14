import katex from 'katex'
import 'katex/dist/katex.min.css'
import { marked } from 'marked'

/** 剥离 OCR 嵌入的 <div><img></div> 图片块 */
function stripEmbeddedImages(text: string): string {
  return text.replace(/<div[^>]*>\s*<img[^>]*\/?\s*>\s*<\/div>/gi, '')
}

/** 判断字符串是否像数学公式（含数学符号才渲染，避免误匹配普通文本） */
function looksLikeMath(s: string): boolean {
  return /[\\^_{}=+\-*/<>|]|\\[a-zA-Z]|\d/.test(s)
}

/**
 * 将原始文本（可能含 LaTeX + Markdown）渲染为 HTML 字符串。
 * `- ` 开头的行保留原样显示，不转为列表圆点。
 * `$...$` 只在内容看起来像数学公式时才用 KaTeX 渲染，避免误匹配普通文本。
 */
export function renderContent(raw: string): string {
  if (!raw) return ''
  let text = stripEmbeddedImages(raw)

  // 行首的 `- ` 转义，阻止 marked 解析为列表项，同时替换为 · 分隔符
  text = text.replace(/^([ \t]*)- /gm, '$1· ')
  // 行中的 ` - ` 也替换为 ` · `（如：技能A - 技能B）
  text = text.replace(/ - /g, ' · ')

  const placeholders: string[] = []

  // $$...$$ 块级公式（块级公式内容通常都是数学，直接渲染）
  text = text.replace(/\$\$([^$]+)\$\$/g, (_m, f) => {
    try {
      const html = katex.renderToString(f.trim(), { displayMode: true, throwOnError: false })
      placeholders.push(html)
      return `KATEXPH${placeholders.length - 1}ENDPH`
    } catch { return _m }
  })

  // $...$ 行内公式（只渲染看起来像数学的内容）
  text = text.replace(/\$([^$\n]{1,100})\$/g, (_m, f) => {
    const trimmed = f.trim()
    if (!looksLikeMath(trimmed)) return _m  // 不像公式，原样保留
    try {
      const html = katex.renderToString(trimmed, { displayMode: false, throwOnError: false })
      placeholders.push(html)
      return `KATEXPH${placeholders.length - 1}ENDPH`
    } catch { return _m }
  })

  const html = marked.parse(text, { async: false, breaks: true }) as string
  return html.replace(/KATEXPH(\d+)ENDPH/g, (_m, idx) => placeholders[Number(idx)] ?? '')
}
