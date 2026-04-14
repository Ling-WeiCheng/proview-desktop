<script setup lang="ts">
import { useResumeStore } from '../../stores/resume'
import SuggestionCard from './SuggestionCard.vue'

const store = useResumeStore()
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200">优化建议</h3>
      <div class="flex gap-3 text-xs font-semibold">
        <span class="text-amber-500">{{ store.pendingCount }} 待处理</span>
        <span class="text-emerald-500">{{ store.acceptedCount }} 已采纳</span>
        <span class="text-slate-400">{{ store.rejectedCount }} 已忽略</span>
      </div>
    </div>

    <div v-if="store.suggestions.length === 0" class="text-center py-10 text-slate-400 text-sm">
      未发现需要优化的内容
    </div>

    <SuggestionCard
      v-for="sug in store.suggestions"
      :key="sug.suggestionId"
      :suggestion="sug"
    />
  </div>
</template>
