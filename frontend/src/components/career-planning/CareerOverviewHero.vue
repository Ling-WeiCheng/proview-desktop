<script setup lang="ts">
import { computed } from 'vue'
import { RefreshCcw, Rocket, Sparkles, TrendingUp } from 'lucide-vue-next'
import type { CareerDashboardStats, CareerProfile } from '../../types/career-planning'
import { useCareerPlanningStore } from '../../stores/careerPlanning'

const props = defineProps<{
  profile: CareerProfile | Record<string, unknown> | null
  stats: CareerDashboardStats
  targetRole: string
  careerGoal: string
  horizonMonths: number
  generating: boolean
}>()

const emit = defineEmits<{
  'update:target-role': [value: string]
  'update:career-goal': [value: string]
  'update:horizon-months': [value: number]
  refresh: []
  generate: []
}>()

const store = useCareerPlanningStore()

const profileData = computed<CareerProfile | null>(() => {
  return props.profile && typeof props.profile === 'object' ? (props.profile as unknown as CareerProfile) : null
})

const strengthTags = computed(() => {
  try {
    const tags = store.profile?.strength_tags as string | undefined
    return tags ? JSON.parse(tags) : []
  } catch {
    return []
  }
})

const gapTags = computed(() => {
  try {
    const tags = store.profile?.gap_tags as string | undefined
    return tags ? JSON.parse(tags) : []
  } catch {
    return []
  }
})

const targetRoleSuggestions = [
  '数据湖架构师',
  '报表自动化工程师',
  '数字健康产品经理',
  '向量数据库工程师',
  '老年科技产品经理',
  'Vue 前端工程师（外包）',
  '客户关系管理系统工程师',
  '无人机飞控工程师',
]

const careerGoalSuggestions = [
  '6 个月内拿到目标岗位 offer',
  '3 个月补齐核心短板并完成作品集',
  '围绕目标岗位完成 2 个可展示项目',
  '持续面试复盘，提升通过率',
]

const horizonSuggestions = [3, 6, 9, 12]

const targetRoleToneClasses = [
  'border-sky-200/90 bg-sky-50/90 text-slate-800 hover:border-sky-300 hover:bg-sky-100/80 dark:border-sky-500/20 dark:bg-sky-500/10 dark:text-slate-100 dark:hover:border-sky-400/40 dark:hover:bg-sky-500/15',
  'border-teal-200/90 bg-teal-50/90 text-slate-800 hover:border-teal-300 hover:bg-teal-100/80 dark:border-teal-500/20 dark:bg-teal-500/10 dark:text-slate-100 dark:hover:border-teal-400/40 dark:hover:bg-teal-500/15',
  'border-cyan-200/90 bg-cyan-50/90 text-slate-800 hover:border-cyan-300 hover:bg-cyan-100/80 dark:border-cyan-500/20 dark:bg-cyan-500/10 dark:text-slate-100 dark:hover:border-cyan-400/40 dark:hover:bg-cyan-500/15',
  'border-emerald-200/90 bg-emerald-50/90 text-slate-800 hover:border-emerald-300 hover:bg-emerald-100/80 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-slate-100 dark:hover:border-emerald-400/40 dark:hover:bg-emerald-500/15',
]

const targetRoleSelectedToneClasses = [
  'border-sky-500 bg-sky-100 text-sky-950 shadow-[0_14px_34px_-22px_rgba(14,165,233,0.65)] dark:border-sky-300/70 dark:bg-sky-500/20 dark:text-white',
  'border-teal-500 bg-teal-100 text-teal-950 shadow-[0_14px_34px_-22px_rgba(20,184,166,0.58)] dark:border-teal-300/70 dark:bg-teal-500/20 dark:text-white',
  'border-cyan-500 bg-cyan-100 text-cyan-950 shadow-[0_14px_34px_-22px_rgba(6,182,212,0.58)] dark:border-cyan-300/70 dark:bg-cyan-500/20 dark:text-white',
  'border-emerald-500 bg-emerald-100 text-emerald-950 shadow-[0_14px_34px_-22px_rgba(16,185,129,0.58)] dark:border-emerald-300/70 dark:bg-emerald-500/20 dark:text-white',
]

const careerGoalToneClasses = [
  'border-amber-200/90 bg-amber-50/90 text-slate-800 hover:border-amber-300 hover:bg-amber-100/80 dark:border-amber-500/20 dark:bg-amber-500/10 dark:text-slate-100 dark:hover:border-amber-400/40 dark:hover:bg-amber-500/15',
  'border-orange-200/90 bg-orange-50/90 text-slate-800 hover:border-orange-300 hover:bg-orange-100/80 dark:border-orange-500/20 dark:bg-orange-500/10 dark:text-slate-100 dark:hover:border-orange-400/40 dark:hover:bg-orange-500/15',
  'border-rose-200/90 bg-rose-50/90 text-slate-800 hover:border-rose-300 hover:bg-rose-100/80 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-slate-100 dark:hover:border-rose-400/40 dark:hover:bg-rose-500/15',
  'border-lime-200/90 bg-lime-50/90 text-slate-800 hover:border-lime-300 hover:bg-lime-100/80 dark:border-lime-500/20 dark:bg-lime-500/10 dark:text-slate-100 dark:hover:border-lime-400/40 dark:hover:bg-lime-500/15',
]

const careerGoalSelectedToneClasses = [
  'border-amber-500 bg-amber-100 text-amber-950 shadow-[0_14px_34px_-22px_rgba(245,158,11,0.58)] dark:border-amber-300/70 dark:bg-amber-500/20 dark:text-white',
  'border-orange-500 bg-orange-100 text-orange-950 shadow-[0_14px_34px_-22px_rgba(249,115,22,0.58)] dark:border-orange-300/70 dark:bg-orange-500/20 dark:text-white',
  'border-rose-500 bg-rose-100 text-rose-950 shadow-[0_14px_34px_-22px_rgba(244,63,94,0.5)] dark:border-rose-300/70 dark:bg-rose-500/20 dark:text-white',
  'border-lime-500 bg-lime-100 text-lime-950 shadow-[0_14px_34px_-22px_rgba(132,204,22,0.5)] dark:border-lime-300/70 dark:bg-lime-500/20 dark:text-white',
]

const horizonToneClasses = [
  'border-emerald-200/90 bg-emerald-50/90 text-slate-800 hover:border-emerald-300 hover:bg-emerald-100/80 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-slate-100 dark:hover:border-emerald-400/40 dark:hover:bg-emerald-500/15',
  'border-teal-200/90 bg-teal-50/90 text-slate-800 hover:border-teal-300 hover:bg-teal-100/80 dark:border-teal-500/20 dark:bg-teal-500/10 dark:text-slate-100 dark:hover:border-teal-400/40 dark:hover:bg-teal-500/15',
  'border-lime-200/90 bg-lime-50/90 text-slate-800 hover:border-lime-300 hover:bg-lime-100/80 dark:border-lime-500/20 dark:bg-lime-500/10 dark:text-slate-100 dark:hover:border-lime-400/40 dark:hover:bg-lime-500/15',
  'border-cyan-200/90 bg-cyan-50/90 text-slate-800 hover:border-cyan-300 hover:bg-cyan-100/80 dark:border-cyan-500/20 dark:bg-cyan-500/10 dark:text-slate-100 dark:hover:border-cyan-400/40 dark:hover:bg-cyan-500/15',
]

const horizonSelectedToneClasses = [
  'border-emerald-500 bg-emerald-100 text-emerald-950 shadow-[0_14px_34px_-22px_rgba(16,185,129,0.58)] dark:border-emerald-300/70 dark:bg-emerald-500/20 dark:text-white',
  'border-teal-500 bg-teal-100 text-teal-950 shadow-[0_14px_34px_-22px_rgba(20,184,166,0.58)] dark:border-teal-300/70 dark:bg-teal-500/20 dark:text-white',
  'border-lime-500 bg-lime-100 text-lime-950 shadow-[0_14px_34px_-22px_rgba(132,204,22,0.5)] dark:border-lime-300/70 dark:bg-lime-500/20 dark:text-white',
  'border-cyan-500 bg-cyan-100 text-cyan-950 shadow-[0_14px_34px_-22px_rgba(6,182,212,0.58)] dark:border-cyan-300/70 dark:bg-cyan-500/20 dark:text-white',
]

function pickTone(base: string[], selected: string[], index: number, active: boolean) {
  const palette = active ? selected : base
  return palette[index % palette.length]
}

const normalizedTargetRole = computed(() => props.targetRole.trim())
const normalizedCareerGoal = computed(() => props.careerGoal.trim())

function setTargetRole(value: string) {
  emit('update:target-role', value)
}

function setCareerGoal(value: string) {
  emit('update:career-goal', value)
}

function setHorizonMonths(value: number) {
  emit('update:horizon-months', value)
}

function isSelectedText(currentValue: string, candidate: string) {
  return currentValue === candidate.trim()
}

function isSelectedNumber(currentValue: number, candidate: number) {
  return currentValue === candidate
}

function emitTargetRole(event: Event) {
  emit('update:target-role', (event.target as HTMLInputElement).value)
}

function emitCareerGoal(event: Event) {
  emit('update:career-goal', (event.target as HTMLInputElement).value)
}

function emitHorizonMonths(event: Event) {
  emit('update:horizon-months', Number((event.target as HTMLInputElement).value || 6))
}
</script>

<script lang="ts">
export default {
  name: 'CareerOverviewHero',
}
</script>

<template>
  <section class="relative overflow-hidden rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-[0_25px_80px_-35px_rgba(15,23,42,0.35)] backdrop-blur dark:border-white/10 dark:bg-[#0C0F17]/90">
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(79,70,229,0.18),_transparent_36%),radial-gradient(circle_at_bottom_left,_rgba(14,165,233,0.15),_transparent_30%)]"></div>
    <div class="relative space-y-5">
      <!-- 标题区 -->
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div class="space-y-2">
          <div class="inline-flex items-center gap-2 rounded-full border border-indigo-200/80 bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-700 dark:border-indigo-500/30 dark:bg-indigo-500/10 dark:text-indigo-200">
            <Sparkles class="h-4 w-4" />
            职业生涯规划
          </div>
          <div class="space-y-3">
            <h1 class="text-3xl font-black tracking-tight text-slate-900 dark:text-white sm:text-4xl">从简历和面试结果出发，生成可执行的职业路径。</h1>
            <p class="max-w-3xl text-sm leading-7 text-slate-600 dark:text-slate-400">这个页面会把现有的简历、面试历史和评估结果合并成一个可跟踪的职业规划面板。你可以直接生成目标岗位路线、补齐技能差距、以及标记阶段任务进度。</p>
          </div>
        </div>
        
        <!-- 顶部统计与操作按钮 -->
        <div class="flex flex-wrap items-center gap-3">
          <div class="grid grid-cols-3 gap-2">
            <div class="rounded-xl border border-sky-200/80 bg-sky-50 px-3 py-2 text-center dark:border-sky-500/20 dark:bg-sky-500/10">
              <p class="text-[10px] font-semibold uppercase text-sky-600 dark:text-sky-200">目标岗位</p>
              <p class="mt-0.5 text-sm font-black text-sky-700 dark:text-sky-100 truncate max-w-[100px]">{{ profileData?.target_role || '未生成' }}</p>
            </div>
            <div class="rounded-xl border border-amber-200/80 bg-amber-50 px-3 py-2 text-center dark:border-amber-500/20 dark:bg-amber-500/10">
              <p class="text-[10px] font-semibold uppercase text-amber-600 dark:text-amber-200">当前阶段</p>
              <p class="mt-0.5 text-sm font-black text-amber-700 dark:text-amber-100 truncate max-w-[100px]">{{ profileData?.current_stage || '等待分析' }}</p>
            </div>
            <div class="rounded-xl border border-emerald-200/80 bg-emerald-50 px-3 py-2 text-center dark:border-emerald-500/20 dark:bg-emerald-500/10">
              <p class="text-[10px] font-semibold uppercase text-emerald-600 dark:text-emerald-200">规划进度</p>
              <p class="mt-0.5 text-sm font-black text-emerald-700 dark:text-emerald-100">{{ stats.progress_rate }}%</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              @click="emit('refresh')"
              class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700 dark:border-white/10 dark:bg-white/5 dark:text-slate-200"
            >
              <RefreshCcw class="h-3.5 w-3.5" />
              刷新
            </button>
            <button
              @click="emit('generate')"
              :disabled="generating"
              class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Rocket class="h-3.5 w-3.5" />
              {{ generating ? '生成中...' : '重新生成规划' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 主内容区：左侧表单 + 右侧能力分析 -->
      <div class="grid gap-6 lg:grid-cols-[1fr_320px]">
        <!-- 左侧：快速选择表单 -->
        <div class="space-y-4 rounded-2xl border border-slate-200/80 bg-white/80 p-4 shadow-sm dark:border-white/10 dark:bg-white/5">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p class="text-sm font-bold text-slate-900 dark:text-white">快速选择</p>
              <p class="text-xs text-slate-500 dark:text-slate-400">点击卡片即可填入表单</p>
            </div>
            <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-500 dark:border-white/10 dark:bg-white/5 dark:text-slate-400">
              单选卡片
            </span>
          </div>

          <!-- 目标岗位 -->
          <div class="space-y-2">
            <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">目标岗位</div>
            <div class="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
              <button
                v-for="(role, index) in targetRoleSuggestions"
                :key="role"
                type="button"
                @click="setTargetRole(role)"
                class="group relative overflow-hidden rounded-xl border px-3 py-2.5 text-left transition duration-200"
                :class="[
                  pickTone(targetRoleToneClasses, targetRoleSelectedToneClasses, index, isSelectedText(normalizedTargetRole, role)),
                  isSelectedText(normalizedTargetRole, role) ? 'translate-y-[-1px]' : 'hover:translate-y-[-1px]',
                ]"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="text-xs font-semibold leading-5 truncate">{{ role }}</span>
                  <span
                    class="h-2 w-2 shrink-0 rounded-full transition"
                    :class="isSelectedText(normalizedTargetRole, role) ? 'bg-sky-600 dark:bg-sky-300' : 'bg-slate-300 dark:bg-slate-600'"
                  ></span>
                </div>
              </button>
            </div>
          </div>

          <!-- 职业目标 -->
          <div class="space-y-2">
            <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">职业目标</div>
            <div class="grid gap-2 sm:grid-cols-2">
              <button
                v-for="(goal, index) in careerGoalSuggestions"
                :key="goal"
                type="button"
                @click="setCareerGoal(goal)"
                class="rounded-xl border px-3 py-2.5 text-left transition duration-200"
                :class="[
                  pickTone(careerGoalToneClasses, careerGoalSelectedToneClasses, index, isSelectedText(normalizedCareerGoal, goal)),
                  isSelectedText(normalizedCareerGoal, goal) ? 'translate-y-[-1px]' : 'hover:translate-y-[-1px]',
                ]"
              >
                <div class="flex items-start gap-2">
                  <span
                    class="mt-0.5 h-2 w-2 shrink-0 rounded-full transition"
                    :class="isSelectedText(normalizedCareerGoal, goal) ? 'bg-amber-600 dark:bg-amber-300' : 'bg-slate-300 dark:bg-slate-600'"
                  ></span>
                  <span class="text-xs font-semibold leading-4">{{ goal }}</span>
                </div>
              </button>
            </div>
          </div>

          <!-- 周期选择 -->
          <div class="space-y-2">
            <div class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">规划周期</div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="(month, index) in horizonSuggestions"
                :key="month"
                type="button"
                @click="setHorizonMonths(month)"
                class="inline-flex min-w-[4rem] items-center justify-center rounded-full border px-3 py-1.5 text-xs font-semibold transition"
                :class="[
                  pickTone(horizonToneClasses, horizonSelectedToneClasses, index, isSelectedNumber(horizonMonths, month)),
                  isSelectedNumber(horizonMonths, month) ? 'translate-y-[-1px]' : 'hover:translate-y-[-1px]',
                ]"
              >
                {{ month }}个月
              </button>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="grid gap-3 sm:grid-cols-3">
            <label class="space-y-1">
              <span class="text-xs font-semibold text-slate-600 dark:text-slate-300">目标岗位</span>
              <input
                :value="targetRole"
                type="text"
                placeholder="输入目标..."
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-900 outline-none transition focus:border-indigo-400 focus:bg-white dark:border-white/10 dark:bg-white/5 dark:text-white"
                @input="emitTargetRole"
              />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-semibold text-slate-600 dark:text-slate-300">职业目标</span>
              <input
                :value="careerGoal"
                type="text"
                placeholder="输入目标..."
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-900 outline-none transition focus:border-indigo-400 focus:bg-white dark:border-white/10 dark:bg-white/5 dark:text-white"
                @input="emitCareerGoal"
              />
            </label>
            <label class="space-y-1">
              <span class="text-xs font-semibold text-slate-600 dark:text-slate-300">周期（月）</span>
              <input
                :value="horizonMonths"
                type="number"
                min="3"
                max="12"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-900 outline-none transition focus:border-indigo-400 focus:bg-white dark:border-white/10 dark:bg-white/5 dark:text-white"
                @input="emitHorizonMonths"
              />
            </label>
          </div>
        </div>

        <!-- 右侧：能力分析面板 -->
        <div class="space-y-3">
          <!-- 总体画像分数 -->
          <div class="rounded-2xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50 to-white p-4 dark:border-indigo-500/20 dark:from-indigo-500/10 dark:to-[#0C0F17]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-indigo-600 dark:text-indigo-200">总体画像分数</p>
                <p class="mt-1 text-3xl font-black text-indigo-700 dark:text-indigo-100">{{ Number(profileData?.overall_score || 0).toFixed(1) }}</p>
              </div>
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 text-white shadow-lg">
                <TrendingUp class="h-5 w-5" />
              </div>
            </div>
            <div class="mt-3 flex gap-2">
              <div class="flex-1 rounded-xl bg-white/80 p-2 text-center dark:bg-[#0B1220]">
                <p class="text-[10px] text-slate-500">任务</p>
                <p class="mt-0.5 text-sm font-bold text-slate-900 dark:text-white">{{ stats.active_task_count }}</p>
              </div>
              <div class="flex-1 rounded-xl bg-white/80 p-2 text-center dark:bg-[#0B1220]">
                <p class="text-[10px] text-slate-500">计划</p>
                <p class="mt-0.5 text-sm font-bold text-slate-900 dark:text-white">{{ stats.plan_count }}</p>
              </div>
              <div class="flex-1 rounded-xl bg-white/80 p-2 text-center dark:bg-[#0B1220]">
                <p class="text-[10px] text-slate-500">完成率</p>
                <p class="mt-0.5 text-sm font-bold text-emerald-600">{{ stats.progress_rate }}%</p>
              </div>
            </div>
          </div>

          <!-- 优势能力 -->
          <div class="rounded-2xl border border-emerald-200/80 bg-gradient-to-br from-emerald-50/80 to-white p-3 dark:border-emerald-500/20 dark:from-emerald-500/10 dark:to-[#0C0F17]">
            <div class="flex items-center gap-2 mb-2">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300">
                💪
              </div>
              <p class="text-xs font-bold text-slate-700 dark:text-white">优势能力</p>
            </div>
            <div class="flex flex-wrap gap-1">
              <span 
                v-for="tag in strengthTags" 
                :key="tag"
                class="rounded-full px-2 py-0.5 text-[10px] font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300"
              >
                {{ tag }}
              </span>
              <span v-if="!strengthTags.length" class="text-[10px] text-slate-400">暂无数据</span>
            </div>
          </div>

          <!-- 待提升项 -->
          <div class="rounded-2xl border border-amber-200/80 bg-gradient-to-br from-amber-50/80 to-white p-3 dark:border-amber-500/20 dark:from-amber-500/10 dark:to-[#0C0F17]">
            <div class="flex items-center gap-2 mb-2">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-300">
                🎯
              </div>
              <p class="text-xs font-bold text-slate-700 dark:text-white">待提升项</p>
            </div>
            <div class="flex flex-wrap gap-1">
              <span 
                v-for="tag in gapTags" 
                :key="tag"
                class="rounded-full px-2 py-0.5 text-[10px] font-medium bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300"
              >
                {{ tag }}
              </span>
              <span v-if="!gapTags.length" class="text-[10px] text-slate-400">暂无数据</span>
            </div>
          </div>

          <!-- 数据摘要 -->
          <div class="rounded-2xl border border-slate-200/80 bg-white/80 p-3 dark:border-white/10 dark:bg-white/5">
            <div class="flex items-center gap-2 mb-2">
              <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-100 text-slate-600 dark:bg-white/10 dark:text-slate-300">
                📊
              </div>
              <p class="text-xs font-bold text-slate-700 dark:text-white">数据摘要</p>
            </div>
            <div class="space-y-1.5 text-[11px]">
              <div class="flex justify-between">
                <span class="text-slate-500">计划总数</span>
                <span class="font-semibold text-slate-700 dark:text-slate-200">{{ store.stats.plan_count }} 个</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">已完成任务</span>
                <span class="font-semibold text-emerald-600">{{ store.stats.completed_task_count }} 个</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">当前活跃</span>
                <span class="font-semibold text-indigo-600">{{ store.stats.active_task_count }} 个</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
