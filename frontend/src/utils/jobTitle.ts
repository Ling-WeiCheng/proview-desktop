function decodeLegacyMojibake(value: string) {
  const binary = globalThis.atob(value)
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

const LEGACY_GARBLED_SENIOR_FRONTEND_TITLE_A = decodeLegacyMojibake(
  '5qWC5qiG6aqC5Zus5bSc5ayl5LyC54C14oaC4oCT6Za45qyS5Z615rW85oSu57Kz54Cj7oeO',
)
const LEGACY_GARBLED_SENIOR_FRONTEND_TITLE_B = decodeLegacyMojibake(
  '5qWg5qiH5rW36Y2Z5qiA5Zus7oGs5a+u7pKC5bGd6Y+C7oCX5aCu55KHz7flmp8=',
)

// Keep these legacy mojibake values to normalize already-persisted dirty data.
const GARBLED_JOB_TITLE_MAP: Record<string, string> = {
  [LEGACY_GARBLED_SENIOR_FRONTEND_TITLE_A]: '高级前端开发工程师',
  [LEGACY_GARBLED_SENIOR_FRONTEND_TITLE_B]: '高级前端开发工程师',
}

export function normalizeJobTitle(value: string | null | undefined): string {
  if (!value) return ''
  const trimmed = value.trim()
  if (!trimmed) return ''
  return GARBLED_JOB_TITLE_MAP[trimmed] || trimmed
}

export function normalizeSessionListItem<T extends { position?: string | null }>(session: T): T {
  if (!session || !session.position) return session
  return {
    ...session,
    position: normalizeJobTitle(session.position),
  }
}

export function normalizeSessionDetail<T extends { session: { position?: string | null } }>(detail: T): T {
  if (!detail?.session) return detail
  return {
    ...detail,
    session: normalizeSessionListItem(detail.session),
  }
}
