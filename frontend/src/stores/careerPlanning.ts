import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  appendCareerTaskLog,
  getCareerDocs,
  generateCareerPlan,
  getCareerDashboard,
  listCareerPlans,
  getCareerPlanningErrorMessage,
  updateCareerTask,
} from '../services/careerPlanning'
import type {
  CareerDashboardData,
  CareerPlanningDocument,
  CareerPlan,
  CareerTask,
  GenerateCareerPlanPayload,
  UpdateCareerTaskPayload,
} from '../types/career-planning'

export const useCareerPlanningStore = defineStore('careerPlanning', () => {
  const dashboard = ref<CareerDashboardData | null>(null)
  const plans = ref<CareerPlan[]>([])
  const loading = ref(false)
  const generating = ref(false)
  const docsLoading = ref(false)
  const error = ref('')
  const docsError = ref('')
  const targetRole = ref('')
  const careerGoal = ref('')
  const horizonMonths = ref(6)
  const documents = ref<CareerPlanningDocument[]>([])

  const currentPlan = computed(() => dashboard.value?.current_plan || plans.value[0] || null)
  const profile = computed(() => dashboard.value?.profile || null)
  const milestones = computed(() => dashboard.value?.milestones || [])
  const tasks = computed(() => dashboard.value?.tasks || [])
  const recommendations = computed(() => dashboard.value?.recommendations || [])
  const stats = computed(() => dashboard.value?.stats || {
    plan_count: 0,
    active_task_count: 0,
    completed_task_count: 0,
    progress_rate: 0,
  })

  function applyDashboard(data: CareerDashboardData) {
    dashboard.value = data
    plans.value = data.plans || []
    if (data.profile && typeof data.profile === 'object' && 'target_role' in data.profile) {
      targetRole.value = String((data.profile as { target_role?: string }).target_role || targetRole.value)
    }
  }

  async function loadDashboard(options?: { force?: boolean }) {
    loading.value = true
    error.value = ''
    try {
      const response = await getCareerDashboard({ force: options?.force })
      if (response.status !== 'success') {
        throw new Error(response.message || '加载职业规划失败')
      }
      applyDashboard(response.data)
    } catch (err) {
      error.value = getCareerPlanningErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function refreshPlans(options?: { force?: boolean }) {
    try {
      const response = await listCareerPlans({ force: options?.force })
      if (response.status === 'success') {
        plans.value = response.data.plans || []
      }
    } catch (err) {
      error.value = getCareerPlanningErrorMessage(err)
    }
  }

  async function loadDocs(options?: { force?: boolean }) {
    docsLoading.value = true
    docsError.value = ''
    try {
      const response = await getCareerDocs({ force: options?.force })
      if (response.status !== 'success') {
        throw new Error(response.message || '加载职业规划文档失败')
      }
      documents.value = response.data.documents || []
    } catch (err) {
      docsError.value = getCareerPlanningErrorMessage(err)
    } finally {
      docsLoading.value = false
    }
  }

  async function createPlan(payload?: GenerateCareerPlanPayload) {
    generating.value = true
    error.value = ''
    try {
      const response = await generateCareerPlan({
        target_role: payload?.target_role ?? targetRole.value,
        career_goal: payload?.career_goal ?? careerGoal.value,
        horizon_months: payload?.horizon_months ?? horizonMonths.value,
        refresh: payload?.refresh ?? true,
      })
      if (response.status !== 'success') {
        throw new Error(response.message || '生成职业规划失败')
      }
      applyDashboard(response.data)
      return response.data
    } catch (err) {
      error.value = getCareerPlanningErrorMessage(err)
      throw err
    } finally {
      generating.value = false
    }
  }

  async function patchTask(taskId: number, payload: UpdateCareerTaskPayload) {
    const response = await updateCareerTask(taskId, payload)
    if (response.status !== 'success') {
      throw new Error(response.message || '更新任务失败')
    }
    applyDashboard(response.data)
    return response.data
  }

  async function logTask(taskId: number, payload: UpdateCareerTaskPayload) {
    const response = await appendCareerTaskLog(taskId, payload)
    if (response.status !== 'success') {
      throw new Error(response.message || '记录任务进度失败')
    }
    applyDashboard(response.data)
    return response.data
  }

  function selectPlan(planId: number) {
    const selected = plans.value.find((plan) => plan.id === planId)
    if (!selected) return
    dashboard.value = {
      ...(dashboard.value || {}),
      current_plan: selected,
    } as CareerDashboardData
  }

  function getTaskById(taskId: number): CareerTask | undefined {
    return tasks.value.find((task) => task.id === taskId)
  }

  return {
    dashboard,
    plans,
    loading,
    generating,
    docsLoading,
    error,
    docsError,
    targetRole,
    careerGoal,
    horizonMonths,
    documents,
    currentPlan,
    profile,
    milestones,
    tasks,
    recommendations,
    stats,
    loadDashboard,
    refreshPlans,
    loadDocs,
    createPlan,
    patchTask,
    logTask,
    selectPlan,
    getTaskById,
  }
})
