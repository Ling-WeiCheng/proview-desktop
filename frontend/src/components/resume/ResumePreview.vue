<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Pencil, Check, GripVertical, MessageSquare } from 'lucide-vue-next'
import { useResumeStore } from '../../stores/resume'

const store = useResumeStore()
const editingId = ref<string | null>(null)
const editContent = ref('')
const editTitle = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const dragIndex = ref<number | null>(null)

const emit = defineEmits<{ 'scroll-to-suggestion': [sectionId: string] }>()

const sectionTypeLabel: Record<string, string> = {
  personal_info: '个人信息',
  education: '教育背景',
  experience: '工作经历',
  skills: '技能特长',
  projects: '项目经历',
  certifications: '证书资质',
  other: '其他'
}

function sectionStatus(sectionId: string) {
  const related = store.suggestions.filter(s => s.targetBlockId === sectionId)
  if (related.length === 0) return 'clean'
  if (related.every(s => s.status === 'ACCEPTED')) return 'accepted'
  if (related.some(s => s.status === 'PENDING')) return 'pending'
  return 'rejected'
}

function pendingCount(sectionId: string) {
  return store.suggestions.filter(
    s => s.targetBlockId === sectionId && s.status === 'PENDING'
  ).length
}

async function startEdit(sectionId: string, title: string, content: string) {
  editingId.value = sectionId
  editTitle.value = title
  editContent.value = content
  await nextTick()
  autoResize()
  textareaRef.value?.focus()
}

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

function saveEdit(sectionId: string) {
  store.updateSectionTitle(sectionId, editTitle.value)
  store.updateSectionContent(sectionId, editContent.value)
  editingId.value = null
}

function onDragStart(index: number) {
  dragIndex.value = index
}

function onDragOver(e: DragEvent, index: number) {
  e.preventDefault()
  if (dragIndex.value === null || dragIndex.value === index) return
  store.reorderSections(dragIndex.value, index)
  dragIndex.value = index
}

function onDragEnd() {
  dragIndex.value = null
}
</script>

<template>
  <div class="space-y-3">
    <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-2">简历白板编辑</h3>

    <div
      v-for="(section, idx) in store.sections"
      :key="section.id"
      draggable="true"
      @dragstart="onDragStart(idx)"
      @dragover="onDragOver($event, idx)"
      @dragend="onDragEnd"
      class="glass-panel rounded-2xl p-4 transition-all group"
      :class="{
        'ring-2 ring-amber-400/50': sectionStatus(section.id) === 'pending',
        'ring-2 ring-emerald-400/50': sectionStatus(section.id) === 'accepted',
        'opacity-50 scale-95': dragIndex === idx,
      }"
    >
      <!-- 卡片头部 -->
      <div class="flex items-center gap-2 mb-2">
        <GripVertical class="w-4 h-4 text-slate-300 dark:text-slate-600 cursor-grab opacity-0 group-hover:opacity-100 transition-opacity" />
        <span class="text-xs font-bold rounded-full px-2 py-0.5 bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
          {{ sectionTypeLabel[section.type] || section.type }}
        </span>

        <!-- 编辑模式：标题输入 -->
        <input
          v-if="editingId === section.id"
          v-model="editTitle"
          class="flex-1 text-sm font-bold bg-transparent border-b border-primary outline-none text-slate-700 dark:text-slate-200"
        />
        <span v-else class="flex-1 text-sm font-bold text-slate-700 dark:text-slate-200">{{ section.title }}</span>

        <!-- 建议 badge -->
        <button
          v-if="pendingCount(section.id) > 0 && editingId !== section.id"
          @click="emit('scroll-to-suggestion', section.id)"
          class="inline-flex items-center gap-1 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 px-2 py-0.5 text-xs font-bold"
        >
          <MessageSquare class="w-3 h-3" /> {{ pendingCount(section.id) }}
        </button>

        <!-- 编辑/保存按钮 -->
        <button
          v-if="editingId === section.id"
          @click="saveEdit(section.id)"
          class="p-1 rounded-lg bg-emerald-100 text-emerald-600 hover:bg-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400"
        >
          <Check class="w-4 h-4" />
        </button>
        <button
          v-else
          @click="startEdit(section.id, section.title, section.content)"
          class="p-1 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-primary dark:hover:bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Pencil class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- 内容区域 -->
      <div v-if="editingId === section.id">
        <textarea
          ref="textareaRef"
          v-model="editContent"
          @input="autoResize"
          class="w-full text-sm bg-white/50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl p-3 outline-none resize-none leading-relaxed text-slate-700 dark:text-slate-200 focus:ring-2 focus:ring-primary/30"
          rows="4"
        />
      </div>
      <div v-else class="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-wrap leading-relaxed cursor-pointer hover:bg-slate-50/50 dark:hover:bg-white/[0.02] rounded-lg p-1 -m-1 transition-colors"
        @click="startEdit(section.id, section.title, section.content)"
      >
        {{ section.content }}
      </div>
    </div>

    <div v-if="store.sections.length === 0" class="text-center py-10 text-slate-400 text-sm">
      暂无简历内容
    </div>
  </div>
</template>