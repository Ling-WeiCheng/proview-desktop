/**
 * SSE (Server-Sent Events) 流式请求工具
 * 用于接收后端 LLM 思考过程的实时输出
 */

export interface EvalDraftUpdate {
  turn: number
  strength?: string
  weakness?: string
  note?: string
}

export interface SSECallbacks {
  onStage?: (stage: string) => void
  onThinking?: (chunk: string) => void
  onContent?: (chunk: string) => void
  onDone?: (data: any) => void
  onError?: (message: string) => void
  // 评估草稿推送
  onEvalDraft?: (data: EvalDraftUpdate) => void
}

/**
 * 发起 SSE 流式请求（POST）
 * @param url 请求地址
 * @param body 请求体（FormData 或 JSON 对象）
 * @param callbacks 事件回调
 * @param headers 额外请求头
 */
export async function fetchSSE(
  url: string,
  body: FormData | Record<string, any> | string,
  callbacks: SSECallbacks,
  headers: Record<string, string> = {},
  signal?: AbortSignal
): Promise<void> {
  const isFormData = body instanceof FormData
  const fetchHeaders: Record<string, string> = { ...headers }
  if (!isFormData && typeof body !== 'string') {
    fetchHeaders['Content-Type'] = 'application/json'
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: fetchHeaders,
    body: isFormData ? body : typeof body === 'string' ? body : JSON.stringify(body),
    signal,
  })

  if (!response.ok) {
    const text = await response.text()
    let message = text || `HTTP ${response.status}`
    try {
      const json = JSON.parse(text)
      if (json && typeof json === 'object' && typeof json.message === 'string' && json.message.trim()) {
        message = json.message
      }
    } catch {
      // Ignore parse failures and fall back to the raw response body.
    }
    throw new Error(message)
  }

  const reader = response.body?.getReader()
  if (!reader) throw new Error('ReadableStream not supported')

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // 解析 SSE 事件（以 \n\n 分隔）
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || '' // 最后一个可能不完整，保留

    for (const part of parts) {
      if (!part.trim()) continue
      let eventType = 'message'
      let data = ''
      for (const line of part.split('\n')) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          data += line.slice(6)
        }
      }
      if (!data) continue

      try {
        const parsed = JSON.parse(data)
        switch (eventType) {
          case 'stage':
            callbacks.onStage?.(parsed.stage)
            break
          case 'thinking':
            callbacks.onThinking?.(parsed.chunk)
            break
          case 'content':
            callbacks.onContent?.(parsed.chunk)
            break
          case 'done':
            callbacks.onDone?.(parsed)
            break
          case 'error':
            callbacks.onError?.(parsed.message)
            break
          case 'eval_update':
            callbacks.onEvalDraft?.({
              turn: parsed.turn,
              strength: parsed.data?.strength,
              weakness: parsed.data?.weakness,
              note: parsed.data?.note,
            })
            break
        }
      } catch {
        // 忽略解析失败的事件
      }
    }
  }
}
