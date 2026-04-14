<script setup lang="ts">
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import { FileText, Target } from 'lucide-vue-next'

const store = useResumeBuilderStore()

function setMode(mode: 'general' | 'targeted') {
  store.document.mode = mode
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex gap-2">
      <button
        @click="setMode('general')"
        class="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all"
        :class="store.document.mode === 'general'
          ? 'bg-primary text-white shadow-md'
          : 'border border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5'"
      >
        <FileText class="w-4 h-4" />
        通用简历
      </button>
      <button
        @click="setMode('targeted')"
        class="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium transition-all"
        :class="store.document.mode === 'targeted'
          ? 'bg-primary text-white shadow-md'
          : 'border border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5'"
      >
        <Target class="w-4 h-4" />
        特定岗位
      </button>
    </div>
    <textarea
      v-if="store.document.mode === 'targeted'"
      v-model="store.document.targetJd"
      rows="3"
      placeholder="粘贴目标岗位 JD，AI 润色时将针对该岗位优化..."
      class="w-full rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-white/5 px-3 py-2 text-sm text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 resize-none"
    />
  </div>
</template>
