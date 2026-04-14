<script setup lang="ts">
import { ref } from 'vue'
import { FilePlus, Upload } from 'lucide-vue-next'
import ResumeImportModal from '../components/resume-builder/ResumeImportModal.vue'
import { useRouter } from 'vue-router'
import { useResumeBuilderStore } from '../stores/resumeBuilder'

const router = useRouter()
const store = useResumeBuilderStore()
const showImportModal = ref(false)

/**
 * 新建空白简历
 */
function createBlankResume() {
  // 清空当前文档，加载默认模板
  store.clearDraft()
  store.loadDraft()  // 加载默认数据
  router.push('/resume-builder')
}

/**
 * 导入现有简历
 */
function openImportModal() {
  showImportModal.value = true
}

/**
 * 导入成功后的回调
 */
function handleImportSuccess() {
  showImportModal.value = false
  // 跳转到编辑器
  router.push('/resume-builder')
}
</script>

<template>
  <div class="entry-container">
    <div class="entry-header">
      <h1 class="entry-title">简历生成器</h1>
      <p class="entry-subtitle">选择一种方式开始创建你的专业简历</p>
    </div>

    <div class="entry-cards">
      <!-- 新建空白简历 -->
      <button @click="createBlankResume" class="entry-card">
        <div class="card-icon-wrapper bg-indigo-100 dark:bg-indigo-900/20">
          <FilePlus class="card-icon text-indigo-600 dark:text-indigo-400" />
        </div>
        <h3 class="card-title">新建空白简历</h3>
        <p class="card-desc">从零开始，使用我们的模板创建一份全新的简历</p>
        <div class="card-badge">推荐</div>
      </button>

      <!-- 导入现有简历 -->
      <button @click="openImportModal" class="entry-card">
        <div class="card-icon-wrapper bg-emerald-100 dark:bg-emerald-900/20">
          <Upload class="card-icon text-emerald-600 dark:text-emerald-400" />
        </div>
        <h3 class="card-title">导入现有简历</h3>
        <p class="card-desc">上传你的旧简历，AI 自动提取内容并优化排版</p>
        <div class="card-features">
          <span class="feature-tag">✨ AI 智能解析</span>
          <span class="feature-tag">🎨 自动排版</span>
        </div>
      </button>
    </div>

    <!-- 导入弹窗 -->
    <ResumeImportModal
      v-if="showImportModal"
      @success="handleImportSuccess"
      @cancel="showImportModal = false"
    />
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.entry-container {
  @apply min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800;
}

.entry-header {
  @apply text-center mb-12;
}

.entry-title {
  @apply text-4xl font-bold text-slate-900 dark:text-white mb-3;
}

.entry-subtitle {
  @apply text-slate-600 dark:text-slate-400;
}

.entry-cards {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full;
}

.entry-card {
  @apply relative p-8 bg-white dark:bg-slate-800 rounded-2xl border-2 border-slate-200 dark:border-slate-700 transition-all text-left;
  @apply hover:border-indigo-500 hover:shadow-xl hover:-translate-y-1;
}

.card-icon-wrapper {
  @apply w-16 h-16 rounded-2xl flex items-center justify-center mb-4;
}

.card-icon {
  @apply w-8 h-8;
}

.card-title {
  @apply text-xl font-bold text-slate-900 dark:text-white mb-2;
}

.card-desc {
  @apply text-sm text-slate-600 dark:text-slate-400 leading-relaxed;
}

.card-badge {
  @apply absolute top-4 right-4 px-3 py-1 bg-indigo-500 text-white text-xs font-medium rounded-full;
}

.card-features {
  @apply flex gap-2 mt-4;
}

.feature-tag {
  @apply text-xs px-2 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full;
}
</style>
