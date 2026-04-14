<script setup lang="ts">
import { useResumeStore } from '../stores/resume'
import { useResumeQuestionnaireStore } from '../stores/resumeQuestionnaire'
import ResumeUploader from '../components/resume/ResumeUploader.vue'
import ResumeWorkspace from '../components/resume/ResumeWorkspace.vue'
import CatLoading from '../components/CatLoading.vue'
import { RotateCcw, CheckCircle } from 'lucide-vue-next'

const store = useResumeStore()
const questionnaireStore = useResumeQuestionnaireStore()

function handleReset() {
  store.reset()
  questionnaireStore.reset()
}
</script>

<template>
  <div class="min-h-[80vh]">
    <CatLoading
      v-if="store.phase === 'exporting'"
      variant="corner"
      :blocking="false"
      message="正在导出优化后的简历"
      stage="你仍然可以继续查看当前优化结果"
    />

    <ResumeUploader v-if="store.phase === 'upload' || store.phase === 'analyzing'" />

    <ResumeWorkspace v-else-if="store.phase === 'review' || store.phase === 'exporting'" />

    <div v-else-if="store.phase === 'done'" class="flex min-h-[80vh] flex-col items-center justify-center fade-in">
      <CheckCircle class="mb-4 h-16 w-16 text-emerald-500" />
      <h2 class="mb-2 text-2xl font-bold text-slate-800 dark:text-white">导出成功</h2>
      <p class="mb-6 text-slate-500 dark:text-slate-400">优化后的简历 PDF 已下载到本地</p>
      <button
        @click="handleReset"
        class="flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-bold text-white shadow-lg shadow-primary/30 transition-all hover:shadow-xl"
      >
        <RotateCcw class="h-4 w-4" />
        优化另一份简历
      </button>
    </div>
  </div>
</template>
