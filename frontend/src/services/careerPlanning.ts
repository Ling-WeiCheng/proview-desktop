import api from './api'
import type {
  CareerDocsResponse,
  CareerDocumentResponse,
  CareerListPlansResponse,
  CareerPlanDetailResponse,
  CareerDashboardResponse,
  GenerateCareerPlanPayload,
  UpdateCareerTaskPayload,
} from '../types/career-planning'

export interface CareerRequestOptions {
  force?: boolean
}

type CacheEntry<T> = {
  expiresAt: number
  promise?: Promise<T>
  value?: T
}

const CAREER_CACHE_TTL_MS = 30_000
const careerCache = new Map<string, CacheEntry<unknown>>()

function cacheKey(method: string, url: string, payload?: unknown) {
  return `${method}:${url}:${JSON.stringify(payload ?? {})}`
}

function isCacheFresh(entry: CacheEntry<unknown>) {
  return Boolean(entry.value) && entry.expiresAt > Date.now()
}

function clearCareerCache(prefix?: string) {
  if (!prefix) {
    careerCache.clear()
    return
  }

  for (const key of careerCache.keys()) {
    if (key.includes(prefix)) {
      careerCache.delete(key)
    }
  }
}

function normalizeCareerApiError(error: unknown) {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response?: { data?: { message?: string; error?: string } } }).response
    return response?.data?.message || response?.data?.error || '职业规划服务请求失败'
  }
  return error instanceof Error ? error.message : '职业规划服务请求失败'
}

function normalizeGeneratePayload(payload: GenerateCareerPlanPayload = {}): Required<GenerateCareerPlanPayload> {
  const horizonRaw = Number(payload.horizon_months ?? 6)
  const parsedHorizon = Number.isFinite(horizonRaw) ? Math.trunc(horizonRaw) : 6
  return {
    target_role: String(payload.target_role ?? '').trim(),
    career_goal: String(payload.career_goal ?? '').trim(),
    horizon_months: Math.min(12, Math.max(3, parsedHorizon || 6)),
    refresh: Boolean(payload.refresh ?? true),
  }
}

async function readCareerResource<T>(method: 'GET', url: string, loader: () => Promise<T>, options: CareerRequestOptions = {}) {
  const key = cacheKey(method, url)
  const existing = careerCache.get(key) as CacheEntry<T> | undefined

  if (!options.force && existing && isCacheFresh(existing)) {
    return existing.value as T
  }

  if (!options.force && existing?.promise) {
    return existing.promise
  }

  const pending = loader().then((value) => {
    careerCache.set(key, { value, expiresAt: Date.now() + CAREER_CACHE_TTL_MS })
    return value
  })

  careerCache.set(key, { promise: pending, expiresAt: Date.now() + CAREER_CACHE_TTL_MS })
  return pending
}

function invalidateCareerCache(prefix?: string) {
  clearCareerCache(prefix)
}

/**
 * Normalize and centralize career-planning API failures for the UI layer.
 */
export function getCareerPlanningErrorMessage(error: unknown) {
  return normalizeCareerApiError(error)
}

/**
 * Fetch the current dashboard snapshot. Results are cached briefly to reduce
 * repeat network traffic when users switch between sub-pages.
 */
export async function getCareerDashboard(options: CareerRequestOptions = {}) {
  return readCareerResource('GET', '/api/career/dashboard', async () => {
    const response = await api.get<CareerDashboardResponse>('/api/career/dashboard')
    return response.data
  }, options)
}

/**
 * Load the plan list used by the roadmap/sidebar views.
 */
export async function listCareerPlans(options: CareerRequestOptions = {}) {
  return readCareerResource('GET', '/api/career/plans', async () => {
    const response = await api.get<CareerListPlansResponse>('/api/career/plans')
    return response.data
  }, options)
}

/**
 * Load the career document catalog.
 */
export async function getCareerDocs(options: CareerRequestOptions = {}) {
  return readCareerResource('GET', '/api/career/docs', async () => {
    const response = await api.get<CareerDocsResponse>('/api/career/docs')
    return response.data
  }, options)
}

/**
 * Load a single document detail view.
 */
export async function getCareerDoc(docId: string, options: CareerRequestOptions = {}) {
  return readCareerResource('GET', `/api/career/docs/${docId}`, async () => {
    const response = await api.get<CareerDocumentResponse>(`/api/career/docs/${docId}`)
    return response.data
  }, options)
}

/**
 * Submit a new generation request after coercing the payload into the backend's
 * expected shape.
 */
export async function generateCareerPlan(payload: GenerateCareerPlanPayload) {
  const normalized = normalizeGeneratePayload(payload)
  const response = await api.post<CareerDashboardResponse>('/api/career/plans/generate', normalized)
  invalidateCareerCache()
  return response.data
}

export async function getCareerPlan(planId: number) {
  const response = await api.get<CareerPlanDetailResponse>(`/api/career/plans/${planId}`)
  return response.data
}

export async function updateCareerTask(taskId: number, payload: UpdateCareerTaskPayload) {
  const response = await api.patch<CareerDashboardResponse>(`/api/career/tasks/${taskId}`, payload)
  invalidateCareerCache()
  return response.data
}

export async function appendCareerTaskLog(taskId: number, payload: UpdateCareerTaskPayload) {
  const response = await api.post<CareerDashboardResponse>(`/api/career/tasks/${taskId}/logs`, payload)
  invalidateCareerCache()
  return response.data
}

export { invalidateCareerCache, normalizeCareerApiError }
