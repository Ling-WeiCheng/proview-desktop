<script setup lang="ts">
import CareerDocsPanel from '../../components/career-planning/CareerDocsPanel.vue'
import { useCareerPlanningStore } from '../../stores/careerPlanning'
import { onMounted } from 'vue'

const store = useCareerPlanningStore()

onMounted(() => {
  // 如果文档还没有加载，则加载
  if (!store.documents.length && !store.docsLoading) {
    store.loadDocs()
  }
})
</script>

<template>
  <section class="space-y-4">
    <!-- 页面介绍卡片 -->
    <div class="rounded-3xl border border-slate-200/80 bg-gradient-to-r from-indigo-500 to-purple-600 p-6 text-white shadow-lg">
      <div class="flex items-start justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wider text-white/80">📚 学习中心</p>
          <h2 class="mt-2 text-2xl font-black">ProView AI 面试学习资源库</h2>
          <p class="mt-2 max-w-2xl text-sm leading-relaxed text-white/90">
            从求职指南到AI面试技巧，从职业规划到发展路径——我们为你在每个阶段准备了最实用的学习资源。
            每份文档都配有可执行的行动项，帮助你将知识转化为实际行动。
          </p>
        </div>
        <div class="hidden md:flex shrink-0">
          <div class="flex -space-x-3">
            <div class="h-10 w-10 rounded-full bg-indigo-300 flex items-center justify-center text-lg">🎯</div>
            <div class="h-10 w-10 rounded-full bg-purple-300 flex items-center justify-center text-lg">📊</div>
            <div class="h-10 w-10 rounded-full bg-pink-300 flex items-center justify-center text-lg">🚀</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档库组件 -->
    <CareerDocsPanel 
      :documents="store.documents" 
      :loading="store.docsLoading" 
      :error="store.docsError" 
      @retry="store.loadDocs({ force: true })"
    />
  </section>
</template>
