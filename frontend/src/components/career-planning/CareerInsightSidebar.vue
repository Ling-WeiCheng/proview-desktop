<script setup lang="ts">
import { computed } from 'vue'
import { FileText, Sparkles, Target } from 'lucide-vue-next'
import type { CareerPlan, CareerProfile, CareerRecommendation } from '../../types/career-planning'

const props = defineProps<{
  profile: CareerProfile | Record<string, unknown> | null
  recommendations: CareerRecommendation[]
  plans: CareerPlan[]
  currentPlan: CareerPlan | Record<string, unknown> | null
}>()

const emit = defineEmits<{
  'select-plan': [planId: number]
}>()

const profileData = computed<CareerProfile | null>(() => {
  return props.profile && typeof props.profile === 'object' ? (props.profile as unknown as CareerProfile) : null
})

const strengthTags = computed(() => {
  try {
    return profileData.value?.strength_tags ? JSON.parse(profileData.value.strength_tags) : []
  } catch {
    return []
  }
})

const gapTags = computed(() => {
  try {
    return profileData.value?.gap_tags ? JSON.parse(profileData.value.gap_tags) : []
  } catch {
    return []
  }
})

const currentPlanId = computed(() => {
  return props.currentPlan && typeof props.currentPlan === 'object' ? (props.currentPlan as unknown as CareerPlan).id : null
})
</script>

<script lang="ts">
export default {
  name: 'CareerInsightSidebar',
}
</script>

<template>
  <div class="space-y-6">
    <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-5 shadow-sm dark:border-white/10 dark:bg-[#0C0F17]/90">
      <div class="flex items-center gap-3">
        <Target class="h-5 w-5 text-indigo-600" />
        <h2 class="text-lg font-black text-slate-900 dark:text-white">能力画像</h2>
      </div>
      <div class="mt-4 space-y-4">
        <div>
          <p class="text-sm font-semibold text-slate-500 dark:text-slate-400">优势标签</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <span v-for="tag in strengthTags" :key="tag" class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-200">{{ tag }}</span>
          </div>
        </div>
        <div>
          <p class="text-sm font-semibold text-slate-500 dark:text-slate-400">差距标签</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <span v-for="tag in gapTags" :key="tag" class="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700 dark:bg-amber-500/15 dark:text-amber-200">{{ tag }}</span>
          </div>
        </div>
        <p class="rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-600 dark:bg-white/5 dark:text-slate-300">
          {{ profileData?.source_summary || '等待后端分析简历和面试历史。' }}
        </p>
      </div>
    </section>

    <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-5 shadow-sm dark:border-white/10 dark:bg-[#0C0F17]/90">
      <div class="flex items-center gap-3">
        <FileText class="h-5 w-5 text-indigo-600" />
        <h2 class="text-lg font-black text-slate-900 dark:text-white">资源建议</h2>
      </div>
      <div class="mt-4 space-y-3">
        <article v-for="recommendation in recommendations" :key="recommendation.title" class="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-white/5">
          <p class="text-xs font-bold uppercase tracking-wide text-indigo-600 dark:text-indigo-300">{{ recommendation.type }}</p>
          <h3 class="mt-2 text-sm font-bold text-slate-900 dark:text-white">{{ recommendation.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{{ recommendation.reason }}</p>
        </article>
      </div>
    </section>

    <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-5 shadow-sm dark:border-white/10 dark:bg-[#0C0F17]/90">
      <div class="flex items-center gap-3">
        <Sparkles class="h-5 w-5 text-indigo-600" />
        <h2 class="text-lg font-black text-slate-900 dark:text-white">计划历史</h2>
      </div>
      <div class="mt-4 space-y-2">
        <button
          v-for="plan in plans.slice(0, 6)"
          :key="plan.id"
          @click="emit('select-plan', plan.id)"
          class="w-full rounded-2xl border px-4 py-3 text-left transition"
          :class="currentPlanId === plan.id ? 'border-indigo-300 bg-indigo-50 dark:border-indigo-500/40 dark:bg-indigo-500/10' : 'border-slate-200 bg-slate-50 dark:border-white/10 dark:bg-white/5'"
        >
          <p class="text-sm font-bold text-slate-900 dark:text-white">{{ plan.target_role }}</p>
          <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ plan.summary }}</p>
        </button>
      </div>
    </section>
  </div>
</template>