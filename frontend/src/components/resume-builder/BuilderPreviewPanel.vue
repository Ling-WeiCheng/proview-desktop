<script setup lang="ts">
import { computed, ref } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import { useResumeExport } from '../../composables/useResumeExport'
import ResumeRenderer from './ResumeRenderer.vue'
import { ZoomIn, ZoomOut, Save, Download, Sparkles } from 'lucide-vue-next'

const store = useResumeBuilderStore()
const { exportResume } = useResumeExport()
const isExporting = ref(false)
const isSaving = ref(false)
const resumePreviewRef = ref<HTMLElement | null>(null)
const preloadPolishDrawer = () => import('./PolishDrawer.vue')

function zoomIn() {
  store.previewZoom = Math.min(1.5, +(store.previewZoom + 0.1).toFixed(2))
}
function zoomOut() {
  store.previewZoom = Math.max(0.4, +(store.previewZoom - 0.1).toFixed(2))
}
const zoomPercent = computed(() => Math.round(store.previewZoom * 100))

async function handleSave() {
  isSaving.value = true
  try {
    store.autoSave()
    await new Promise(resolve => setTimeout(resolve, 500))
  } finally {
    isSaving.value = false
  }
}

async function handleExport() {
  if (!resumePreviewRef.value) {
    alert('预览区域未加载，请稍后重试')
    return
  }

  isExporting.value = true
  try {
    // 获取简历渲染器的 DOM 元素（跳过缩放容器）
    const resumeElement = resumePreviewRef.value.querySelector('.resume-renderer') as HTMLElement
    if (!resumeElement) {
      throw new Error('无法找到简历内容')
    }

    await exportResume(resumeElement, {
      filename: `${store.document.basicInfo.name || '简历'}_${Date.now()}`,
      format: 'pdf',
      quality: 0.95,
    })
  } catch (error: any) {
    console.error('导出失败:', error)
    alert(error.message || '导出失败，请稍后重试')
  } finally {
    isExporting.value = false
  }
}

async function handleOptimize() {
  if (store.isPolishing) {
    return
  }

  store.polishDrawerOpen = false

  await Promise.all([
    store.requestPolish().catch(() => undefined),
    preloadPolishDrawer().catch(() => undefined),
  ])

  store.polishDrawerOpen = true
}
</script>

<template>
  <div class="glass-panel rounded-3xl flex flex-col overflow-hidden h-full">
    <!-- Header -->
    <div class="flex items-center justify-between px-5 py-3 border-b border-slate-200/60 dark:border-white/5">
      <h2 class="text-sm font-bold text-slate-700 dark:text-slate-200">简历实时预览</h2>
      <div class="flex items-center gap-2">
        <!-- AI 优化按钮 -->
        <button
          @click="handleOptimize"
          :disabled="store.isPolishing"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:shadow-lg transition-all disabled:opacity-50"
          title="AI 优化"
        >
          <Sparkles class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">{{ store.isPolishing ? '优化中...' : 'AI 优化' }}</span>
        </button>

        <!-- 保存草稿 -->
        <button
          @click="handleSave"
          :disabled="isSaving || !store.isDirty"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-300 dark:hover:bg-white/10 transition-colors disabled:opacity-50"
          title="保存草稿"
        >
          <Save class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">{{ isSaving ? '保存中...' : '保存' }}</span>
        </button>

        <!-- 导出 PDF -->
        <button
          @click="handleExport"
          :disabled="isExporting"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-primary text-white hover:shadow-lg transition-all disabled:opacity-50"
          title="导出 PDF"
        >
          <Download class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">{{ isExporting ? '导出中...' : '导出' }}</span>
        </button>

        <!-- 缩放控制 -->
        <div class="flex items-center gap-1 ml-2 pl-2 border-l border-slate-200 dark:border-white/10">
          <button
            @click="zoomOut"
            class="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-white/5 transition-colors"
          >
            <ZoomOut class="w-4 h-4" />
          </button>
          <span class="text-xs font-medium text-slate-500 dark:text-slate-400 w-10 text-center tabular-nums">
            {{ zoomPercent }}%
          </span>
          <button
            @click="zoomIn"
            class="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-white/5 transition-colors"
          >
            <ZoomIn class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Scrollable preview area -->
    <div class="flex-1 overflow-auto custom-scroll bg-slate-100/50 dark:bg-[#05050A]/40 p-6">
      <div class="flex justify-center" ref="resumePreviewRef">
        <div
          :style="{ transform: `scale(${store.previewZoom})`, transformOrigin: 'top center' }"
          class="transition-transform duration-150"
        >
          <ResumeRenderer />
        </div>
      </div>
    </div>
  </div>
</template>
