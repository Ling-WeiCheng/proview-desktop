<script setup lang="ts">
import { Palette, Minus, Plus } from 'lucide-vue-next'
import { PRESET_COLORS } from '../../types/resume-builder'
import type { TemplateId } from '../../types/resume-builder'

const props = defineProps<{
  templateId: TemplateId
  themeColor: string
  fontSize: number
  lineHeight: number
  horizontal?: boolean
}>()

const emit = defineEmits<{
  'update:templateId': [id: TemplateId]
  'update:themeColor': [color: string]
  'update:fontSize': [size: number]
  'update:lineHeight': [lh: number]
}>()

const generalTemplates: { id: TemplateId; label: string; desc: string }[] = [
  { id: 'classic', label: '经典', desc: '单栏居中，简洁大方' },
  { id: 'modern', label: '现代', desc: '双栏布局，左侧彩色' },
  { id: 'minimal', label: '极简', desc: '纯文字，干净利落' },
]

const scenarioTemplates: { id: TemplateId; label: string; desc: string }[] = [
  { id: 'fresh', label: '清新', desc: '应届生/考研' },
  { id: 'tech', label: '技术', desc: '程序员/工程师' },
  { id: 'creative', label: '创意', desc: '设计师/运营' },
  { id: 'executive', label: '商务', desc: '产品/销售' },
  { id: 'elegant', label: '雅致', desc: '高端/管理层' },
]

function adjustFontSize(delta: number) {
  emit('update:fontSize', Math.min(18, Math.max(10, props.fontSize + delta)))
}

function adjustLineHeight(delta: number) {
  emit('update:lineHeight', Math.min(2.4, Math.max(1.2, +(props.lineHeight + delta).toFixed(1))))
}
</script>

<template>
  <!-- 竖向（默认，用于侧边栏） -->
  <div v-if="!horizontal" class="space-y-4">
    <!-- General templates -->
    <div>
      <div class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">通用模板</div>
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="t in generalTemplates" :key="t.id"
          @click="emit('update:templateId', t.id)"
          class="rounded-xl border-2 p-3 text-left transition-all"
          :class="templateId === t.id
            ? 'border-primary bg-primary/5 dark:bg-primary/10'
            : 'border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20'"
        >
          <div class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ t.label }}</div>
          <div class="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">{{ t.desc }}</div>
        </button>
      </div>
    </div>

    <!-- Scenario templates -->
    <div>
      <div class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">场景模板</div>
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="t in scenarioTemplates" :key="t.id"
          @click="emit('update:templateId', t.id)"
          class="rounded-xl border-2 p-3 text-left transition-all"
          :class="templateId === t.id
            ? 'border-primary bg-primary/5 dark:bg-primary/10'
            : 'border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20'"
        >
          <div class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ t.label }}</div>
          <div class="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">{{ t.desc }}</div>
        </button>
      </div>
    </div>

    <!-- Color picker -->
    <div>
      <div class="flex items-center gap-2 mb-2">
        <Palette class="w-3.5 h-3.5 text-slate-400" />
        <span class="text-xs font-medium text-slate-500 dark:text-slate-400">主题色</span>
      </div>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="c in PRESET_COLORS" :key="c"
          @click="emit('update:themeColor', c)"
          class="w-6 h-6 rounded-full border-2 transition-transform hover:scale-110"
          :class="themeColor === c ? 'border-primary scale-110' : 'border-transparent'"
          :style="{ background: c }"
        />
      </div>
    </div>

    <!-- Font size & line height -->
    <div class="flex gap-4">
      <div class="flex-1">
        <div class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">字号</div>
        <div class="flex items-center gap-2">
          <button @click="adjustFontSize(-1)" class="ctrl-btn"><Minus class="w-3 h-3" /></button>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-200 w-8 text-center tabular-nums">{{ fontSize }}</span>
          <button @click="adjustFontSize(1)" class="ctrl-btn"><Plus class="w-3 h-3" /></button>
        </div>
      </div>
      <div class="flex-1">
        <div class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">行高</div>
        <div class="flex items-center gap-2">
          <button @click="adjustLineHeight(-0.1)" class="ctrl-btn"><Minus class="w-3 h-3" /></button>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-200 w-8 text-center tabular-nums">{{ lineHeight }}</span>
          <button @click="adjustLineHeight(0.1)" class="ctrl-btn"><Plus class="w-3 h-3" /></button>
        </div>
      </div>
    </div>
  </div>

  <!-- 横向（用于顶部工具栏） -->
  <div v-else class="flex flex-wrap items-start gap-x-6 gap-y-3">
    <!-- 模板 -->
    <div>
      <div class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">模板</div>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="t in [...generalTemplates, ...scenarioTemplates]" :key="t.id"
          @click="emit('update:templateId', t.id)"
          class="rounded-lg border-2 px-2.5 py-1 text-xs font-medium transition-all"
          :class="templateId === t.id
            ? 'border-primary bg-primary/5 text-primary dark:bg-primary/10'
            : 'border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-white/20'"
        >
          {{ t.label }}
        </button>
      </div>
    </div>

    <!-- 主题色 -->
    <div>
      <div class="flex items-center gap-1.5 mb-1.5">
        <Palette class="w-3 h-3 text-slate-400" />
        <span class="text-xs font-medium text-slate-500 dark:text-slate-400">主题色</span>
      </div>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="c in PRESET_COLORS" :key="c"
          @click="emit('update:themeColor', c)"
          class="w-5 h-5 rounded-full border-2 transition-transform hover:scale-110"
          :class="themeColor === c ? 'border-primary scale-110' : 'border-transparent'"
          :style="{ background: c }"
        />
      </div>
    </div>

    <!-- 字号 & 行高 -->
    <div class="flex gap-4">
      <div>
        <div class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">字号</div>
        <div class="flex items-center gap-1.5">
          <button @click="adjustFontSize(-1)" class="ctrl-btn"><Minus class="w-3 h-3" /></button>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-200 w-7 text-center tabular-nums">{{ fontSize }}</span>
          <button @click="adjustFontSize(1)" class="ctrl-btn"><Plus class="w-3 h-3" /></button>
        </div>
      </div>
      <div>
        <div class="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">行高</div>
        <div class="flex items-center gap-1.5">
          <button @click="adjustLineHeight(-0.1)" class="ctrl-btn"><Minus class="w-3 h-3" /></button>
          <span class="text-sm font-medium text-slate-700 dark:text-slate-200 w-7 text-center tabular-nums">{{ lineHeight }}</span>
          <button @click="adjustLineHeight(0.1)" class="ctrl-btn"><Plus class="w-3 h-3" /></button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ctrl-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  color: #64748b;
  transition: all 0.15s;
}
.ctrl-btn:hover { background: #f1f5f9; color: #334155; }
:is(.dark) .ctrl-btn { border-color: rgba(255,255,255,0.1); color: #94a3b8; }
:is(.dark) .ctrl-btn:hover { background: rgba(255,255,255,0.05); color: #e2e8f0; }
</style>
