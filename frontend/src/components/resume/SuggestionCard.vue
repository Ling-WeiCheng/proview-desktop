<script setup lang="ts">
import { computed } from 'vue'
import { Check, X, AlertTriangle } from 'lucide-vue-next'
import type { ResumeSuggestion } from '../../types/resume'
import { useResumeStore } from '../../stores/resume'

const props = defineProps<{ suggestion: ResumeSuggestion }>()
const store = useResumeStore()

const issueColor = computed(() => {
  const map: Record<string, string> = {
    LACK_OF_METRICS: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    WEAK_ACTION_VERB: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    VAGUE_DESCRIPTION: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
    MISSING_STAR: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    ATS_KEYWORD_GAP: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    FORMAT_ISSUE: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  }
  return map[props.suggestion.issueType] ?? 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
})
</script>

<template>
  <div
    class="glass-panel rounded-2xl p-4 transition-all"
    :class="{
      'opacity-50': suggestion.status === 'REJECTED',
      'ring-2 ring-emerald-400/50': suggestion.status === 'ACCEPTED'
    }"
  >
    <!-- 标签 + 状态 -->
    <div class="flex items-center justify-between mb-3">
      <span class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold" :class="issueColor">
        <AlertTriangle class="w-3 h-3" />
        {{ suggestion.issueLabel }}
      </span>
      <span v-if="suggestion.status === 'ACCEPTED'" class="text-xs font-bold text-emerald-500">已采纳</span>
      <span v-else-if="suggestion.status === 'REJECTED'" class="text-xs font-bold text-slate-400">已忽略</span>
    </div>

    <!-- 原文 -->
    <div class="mb-2">
      <div class="text-xs font-semibold text-slate-400 mb-1">原文</div>
      <div class="text-sm text-slate-600 dark:text-slate-300 bg-red-50/50 dark:bg-red-900/10 rounded-lg p-2 line-through decoration-red-300">
        {{ suggestion.originalText }}
      </div>
    </div>

    <!-- 建议 -->
    <div class="mb-2">
      <div class="text-xs font-semibold text-emerald-500 mb-1">优化建议</div>
      <div class="text-sm text-slate-700 dark:text-slate-200 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-lg p-2 font-medium">
        {{ suggestion.suggestedText }}
      </div>
    </div>

    <!-- 理由 -->
    <p class="text-xs text-slate-400 mb-3">{{ suggestion.reason }}</p>

    <!-- 操作按钮 -->
    <div v-if="suggestion.status === 'PENDING'" class="flex gap-2">
      <button
        @click="store.acceptSuggestion(suggestion.suggestionId)"
        class="flex-1 flex items-center justify-center gap-1 rounded-xl bg-emerald-500 py-2 text-xs font-bold text-white transition-colors hover:bg-emerald-600"
      >
        <Check class="w-3.5 h-3.5" /> 采纳
      </button>
      <button
        @click="store.rejectSuggestion(suggestion.suggestionId)"
        class="flex-1 flex items-center justify-center gap-1 rounded-xl bg-slate-200 py-2 text-xs font-bold text-slate-600 transition-colors hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
      >
        <X class="w-3.5 h-3.5" /> 忽略
      </button>
    </div>
  </div>
</template>
