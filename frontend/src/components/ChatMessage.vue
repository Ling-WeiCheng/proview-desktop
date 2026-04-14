<script setup lang="ts">
import { computed } from 'vue'
import { Bot, User } from 'lucide-vue-next'

const props = defineProps<{
  role: 'user' | 'ai'
  content: string
  corrections?: Array<{ original: string; corrected: string }>
}>()

/** 将 content 拆分为普通文本和纠错高亮片段 */
const segments = computed(() => {
  if (!props.corrections?.length) return null
  const parts: Array<{ text: string; corrected?: string }> = []
  let remaining = props.content
  // 按 corrected 词在 content 中的位置依次拆分
  for (const c of props.corrections) {
    const idx = remaining.indexOf(c.corrected)
    if (idx === -1) continue
    if (idx > 0) parts.push({ text: remaining.slice(0, idx) })
    parts.push({ text: c.corrected, corrected: c.original })
    remaining = remaining.slice(idx + c.corrected.length)
  }
  if (remaining) parts.push({ text: remaining })
  return parts.length > 0 ? parts : null
})
</script>

<template>
  <div v-if="role === 'ai'" class="flex gap-4 max-w-[85%] fade-in">
    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 shrink-0 flex items-center justify-center text-white shadow-md">
      <Bot class="w-5 h-5" />
    </div>
    <div class="bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 px-5 py-4 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 dark:border-white/5 leading-relaxed whitespace-pre-line">
      {{ content }}
    </div>
  </div>
  <div v-else class="flex gap-4 max-w-[85%] self-end ml-auto justify-end fade-in">
    <div class="bg-primary text-white px-5 py-4 rounded-2xl rounded-tr-none shadow-md leading-relaxed whitespace-pre-line">
      <template v-if="segments">
        <template v-for="(seg, i) in segments">
          <span v-if="seg.corrected" :key="'c'+i" class="correction-highlight" :title="'语音识别: ' + seg.corrected">{{ seg.text }}</span>
          <span v-else :key="'t'+i">{{ seg.text }}</span>
        </template>
      </template>
      <template v-else>{{ content }}</template>
    </div>
    <div class="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 shrink-0 flex items-center justify-center text-slate-600 dark:text-slate-300 shadow-sm">
      <User class="w-5 h-5" />
    </div>
  </div>
</template>

<style scoped>
.correction-highlight {
  background: rgba(255, 255, 255, 0.25);
  border-bottom: 2px solid rgba(255, 255, 255, 0.7);
  border-radius: 2px;
  padding: 0 2px;
  animation: correction-flash 1.5s ease-out;
  cursor: help;
}

@keyframes correction-flash {
  0% { background: rgba(74, 222, 128, 0.6); }
  50% { background: rgba(74, 222, 128, 0.3); }
  100% { background: rgba(255, 255, 255, 0.25); }
}
</style>
