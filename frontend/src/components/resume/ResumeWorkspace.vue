<script setup lang="ts">
import { ref, computed } from 'vue'
import { Download, Eye, ListChecks, Maximize2, X, Camera, Trash2 } from 'lucide-vue-next'
import { useResumeStore } from '../../stores/resume'
import ResumePreview from './ResumePreview.vue'
import ResumeLivePreview from './ResumeLivePreview.vue'
import SuggestionList from './SuggestionList.vue'
import ResumeRenderer from '../resume-builder/ResumeRenderer.vue'
import ResumeStylePanel from '../resume-builder/ResumeStylePanel.vue'

const store = useResumeStore()
const rightTab = ref<'suggestions' | 'preview'>('suggestions')
const showFullPreview = ref(false)
const showStylePanel = ref(false)
const showFullStylePanel = ref(false)

function scrollToSuggestion(_sectionId: string) {
  rightTab.value = 'suggestions'
}

// 照片上传
const photoInput = ref<HTMLInputElement | null>(null)

function triggerPhotoUpload() {
  photoInput.value?.click()
}

function handlePhotoChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    store.updatePhoto(reader.result as string)
  }
  reader.readAsDataURL(file)
  // 清空 input，允许重复上传同一文件
  ;(e.target as HTMLInputElement).value = ''
}

function removePhoto() {
  store.updatePhoto('')
}

const hasPhoto = computed(() => !!store.builderDocument?.basicInfo?.photoUrl)
</script>

<template>
  <div class="fade-in">
    <!-- 错误提示 -->
    <div v-if="store.error" class="mb-4 rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
      {{ store.error }}
    </div>

    <!-- 顶部工具栏 -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-slate-800 dark:text-white">审核工作台</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          AI 发现了 {{ store.suggestions.length }} 条优化建议，请逐一审核
        </p>
      </div>
      <div class="flex gap-3">
        <button
          @click="store.exportPdf()"
          :disabled="store.phase === 'exporting'"
          class="flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-primary/30 transition-all hover:shadow-xl disabled:opacity-50"
        >
          <Download class="w-4 h-4" />
          {{ store.phase === 'exporting' ? '导出中...' : '导出 PDF' }}
        </button>
      </div>
    </div>

    <!-- 主体区域：flex 列，样式面板在顶部全宽展开 -->
    <div class="flex flex-col gap-4">
      <!-- 样式面板：全宽，在两栏上方展开 -->
      <div
        v-if="showStylePanel && store.builderDocument"
        class="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 p-4"
      >
        <ResumeStylePanel
          horizontal
          :template-id="store.builderDocument.settings.templateId"
          :theme-color="store.builderDocument.settings.themeColor"
          :font-size="store.builderDocument.settings.fontSize"
          :line-height="store.builderDocument.settings.lineHeight"
          @update:template-id="(id) => store.setTemplateId(id)"
          @update:theme-color="(c) => store.setThemeColor(c)"
          @update:font-size="(v) => store.setFontSize(v)"
          @update:line-height="(v) => store.setLineHeight(v)"
        />
      </div>

      <!-- 下方：左右分屏，高度随样式面板动态调整 -->
      <div
        class="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-6"
        :style="{ height: showStylePanel ? 'calc(100vh - 320px)' : 'calc(100vh - 220px)' }"
      >
        <!-- 左侧：简历结构预览 -->
        <div class="overflow-y-auto custom-scroll pr-2 h-full">
          <ResumePreview @scroll-to-suggestion="scrollToSuggestion" />
        </div>

        <!-- 右侧：Tab 切换（建议列表 / 实时预览） -->
        <div class="flex flex-col h-full min-h-0">
          <div class="flex items-center gap-2 mb-4">
            <button
              @click="rightTab = 'suggestions'"
              class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition-all"
              :class="rightTab === 'suggestions'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-slate-100 text-slate-500 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-400 dark:hover:bg-white/10'"
            >
              <ListChecks class="w-3.5 h-3.5" /> 优化建议
            </button>
            <button
              @click="rightTab = 'preview'"
              class="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition-all"
              :class="rightTab === 'preview'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-slate-100 text-slate-500 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-400 dark:hover:bg-white/10'"
            >
              <Eye class="w-3.5 h-3.5" /> 实时预览
            </button>

            <!-- 预览 tab 工具栏 -->
            <template v-if="rightTab === 'preview' && store.builderDocument">
              <div class="ml-auto flex items-center gap-2">
                <!-- 样式面板开关 -->
                <button
                  @click="showStylePanel = !showStylePanel"
                  class="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors"
                  :class="showStylePanel
                    ? 'bg-primary/10 text-primary dark:bg-primary/20'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-400 dark:hover:bg-white/10'"
                >
                  样式
                </button>
                <!-- 放大按钮 -->
                <button
                  @click="showFullPreview = true"
                  class="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-400 dark:hover:bg-white/10 transition-colors"
                  title="放大预览"
                >
                  <Maximize2 class="w-3.5 h-3.5" />
                  放大
                </button>
                <!-- 照片上传 -->
                <button
                  @click="triggerPhotoUpload"
                  class="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-400 dark:hover:bg-white/10 transition-colors"
                  title="上传证件照"
                >
                  <Camera class="w-3.5 h-3.5" />
                  {{ hasPhoto ? '换照片' : '上传照片' }}
                </button>
                <button
                  v-if="hasPhoto"
                  @click="removePhoto"
                  class="flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-medium text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                  title="删除照片"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
                <input ref="photoInput" type="file" accept="image/*" class="hidden" @change="handlePhotoChange" />
              </div>
            </template>
          </div>

          <div class="flex-1 overflow-y-auto custom-scroll pr-2 min-h-0">
            <SuggestionList v-if="rightTab === 'suggestions'" />
            <ResumeLivePreview v-else @open-fullscreen="showFullPreview = true" />
          </div>
        </div>
      </div>
    </div>

    <!-- 全屏预览弹窗 -->
    <Teleport to="body">
      <div v-if="showFullPreview" class="fullscreen-overlay" @click.self="showFullPreview = false">
        <div class="fullscreen-container">
          <!-- 顶栏 -->
          <div class="fullscreen-toolbar">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-200">简历预览</span>
            <div class="flex items-center gap-2">
              <button
                @click="showFullStylePanel = !showFullStylePanel"
                class="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-colors"
                :class="showFullStylePanel
                  ? 'bg-primary/10 text-primary dark:bg-primary/20'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-white/5 dark:text-slate-400 dark:hover:bg-white/10'"
              >
                样式
              </button>
              <button
                @click="showFullPreview = false"
                class="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 transition-colors text-slate-500 dark:text-slate-400"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
          </div>
          <!-- 简历内容 -->
          <div class="fullscreen-scroll custom-scroll">
            <div class="fullscreen-content">
              <div v-if="showFullStylePanel && store.builderDocument" class="fullscreen-style-panel">
                <ResumeStylePanel
                  horizontal
                  :template-id="store.builderDocument.settings.templateId"
                  :theme-color="store.builderDocument.settings.themeColor"
                  :font-size="store.builderDocument.settings.fontSize"
                  :line-height="store.builderDocument.settings.lineHeight"
                  @update:template-id="(id) => store.setTemplateId(id)"
                  @update:theme-color="(c) => store.setThemeColor(c)"
                  @update:font-size="(v) => store.setFontSize(v)"
                  @update:line-height="(v) => store.setLineHeight(v)"
                />
              </div>
              <div class="fullscreen-paper">
                <ResumeRenderer v-if="store.builderDocument" :document="store.builderDocument" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.fullscreen-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fade-in 0.2s ease;
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.fullscreen-container {
  width: 90vw;
  max-width: 860px;
  height: 90vh;
  background: #f8fafc;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}
:root.dark .fullscreen-container,
.dark .fullscreen-container {
  background: #0f0f1a;
}
.fullscreen-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}
:root.dark .fullscreen-toolbar,
.dark .fullscreen-toolbar {
  border-color: rgba(255, 255, 255, 0.06);
}
.fullscreen-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
.fullscreen-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.fullscreen-style-panel {
  width: 100%;
  max-width: 860px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 16px;
}
:root.dark .fullscreen-style-panel,
.dark .fullscreen-style-panel {
  background: rgba(255,255,255,0.04);
  border-color: rgba(255,255,255,0.08);
}
.fullscreen-paper {
  background: white;
  width: 210mm;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
  overflow: visible;
  flex-shrink: 0;
  min-height: 297mm;
}
:root.dark .fullscreen-paper,
.dark .fullscreen-paper {
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.05);
}
</style>
