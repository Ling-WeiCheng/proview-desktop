<script setup lang="ts">
import { computed } from 'vue'
import CareerRoadmapPanel from '../../components/career-planning/CareerRoadmapPanel.vue'
import { useCareerPlanningStore } from '../../stores/careerPlanning'

const store = useCareerPlanningStore()

const completedCount = computed(() => store.milestones.filter(m => m.status === 'completed').length)
const progressPercent = computed(() => store.milestones.length ? Math.round((completedCount.value / store.milestones.length) * 100) : 0)
</script>

<template>
  <section class="space-y-5">
    <!-- 页面标题区 -->
    <div class="relative overflow-hidden rounded-3xl border border-indigo-200/40 bg-gradient-to-br from-indigo-600 via-purple-600 to-cyan-500 p-6 shadow-xl shadow-indigo-500/20">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10"></div>
      <div class="absolute -bottom-5 -right-5 h-24 w-24 rounded-full bg-white/5"></div>
      <div class="relative flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-white/70">🗺️ 路线图</p>
          <h1 class="mt-2 text-3xl font-black tracking-tight text-white">按阶段展开目标、里程碑和预期结果</h1>
          <p class="mt-2 max-w-xl text-sm text-white/80">这是一条从当前状态到目标岗位的线性路线，适合快速检查每一阶段是否已经按计划推进。</p>
        </div>
        <div class="hidden lg:flex items-center gap-4">
          <div class="text-center">
            <p class="text-3xl font-black text-white">{{ completedCount }}/{{ store.milestones.length }}</p>
            <p class="text-xs text-white/70">已完成阶段</p>
          </div>
          <div class="h-12 w-12 rounded-full bg-white/20 flex items-center justify-center">
            <span class="text-xl">📍</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 进度概览 -->
    <div class="rounded-2xl border border-slate-200/80 bg-white/80 p-4 backdrop-blur-sm dark:border-white/10 dark:bg-[#0C0F17]/80">
      <div class="flex items-center justify-between mb-2">
        <p class="text-sm font-semibold text-slate-700 dark:text-white">整体进度</p>
        <p class="text-sm font-bold text-indigo-600 dark:text-indigo-400">{{ progressPercent }}%</p>
      </div>
      <div class="h-2.5 overflow-hidden rounded-full bg-slate-200 dark:bg-white/10">
        <div 
          class="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 transition-all duration-500"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
    </div>

    <!-- 路线图面板 -->
    <CareerRoadmapPanel :milestones="store.milestones" />
  </section>
</template>