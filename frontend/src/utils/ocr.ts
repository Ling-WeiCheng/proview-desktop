export function isReusableOcrText(value?: string | null): boolean {
  const text = (value || '').trim()
  if (!text) return false

  const lowered = text.toLowerCase()
  const invalidMarkers = [
    '[error]',
    '[unavailable]',
    '[not_called]',
    'error:',
    'ocr api',
    'ocr 调用异常',
    'api 令牌未配置',
    '无法连接到ocr',
    '错误:',
  ]

  if (invalidMarkers.some((marker) => lowered.includes(marker))) {
    return false
  }

  if (
    text.includes('解析成功') ||
    text.includes('【解析成功】') ||
    text.includes('以下是提取的内容')
  ) {
    return true
  }

  return text.length >= 200
}
