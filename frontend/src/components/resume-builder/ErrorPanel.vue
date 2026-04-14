<script setup lang="ts">
import { ref, computed } from 'vue'
import { AlertCircle, X, ChevronDown, ChevronUp, Copy, Check } from 'lucide-vue-next'

interface ErrorDetails {
  error_type?: string
  error_message?: string
  traceback?: string
}

interface Props {
  error: string | null
  details?: ErrorDetails | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const expanded = ref(false)
const copied = ref(false)

const hasDetails = computed(() => {
  return props.details && (props.details.error_type || props.details.traceback)
})

async function copyError() {
  const text = `
错误类型: ${props.details?.error_type || 'Unknown'}
错误信息: ${props.error || props.details?.error_message || 'Unknown'}

堆栈跟踪:
${props.details?.traceback || 'No traceback available'}
  `.trim()

  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    copied.value = false
  }
}
</script>

<template>
  <div v-if="error" class="error-panel">
    <div class="error-header">
      <AlertCircle class="error-icon" />
      <div class="error-content">
        <h4 class="error-title">AI 优化失败</h4>
        <p class="error-message">{{ error }}</p>
      </div>
      <button @click="emit('close')" class="error-close">
        <X class="w-4 h-4" />
      </button>
    </div>

    <div v-if="hasDetails" class="error-actions">
      <button @click="expanded = !expanded" class="action-btn">
        <component :is="expanded ? ChevronUp : ChevronDown" class="w-4 h-4" />
        <span>{{ expanded ? '隐藏' : '查看' }}详细信息</span>
      </button>
      <button @click="copyError" class="action-btn">
        <component :is="copied ? Check : Copy" class="w-4 h-4" />
        <span>{{ copied ? '已复制' : '复制错误' }}</span>
      </button>
    </div>

    <div v-if="expanded && details" class="error-details">
      <div v-if="details.error_type" class="detail-item">
        <span class="detail-label">错误类型:</span>
        <code class="detail-value">{{ details.error_type }}</code>
      </div>

      <div v-if="details.traceback" class="detail-item">
        <span class="detail-label">堆栈跟踪:</span>
        <pre class="detail-traceback">{{ details.traceback }}</pre>
      </div>
    </div>

    <div class="error-footer">
      <p class="error-hint">💡 提示：请检查后端日志或联系技术支持</p>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.error-panel {
  @apply bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500/30 rounded-xl overflow-hidden;
}

.error-header {
  @apply flex items-start gap-3 p-4;
}

.error-icon {
  @apply w-5 h-5 text-red-500 shrink-0 mt-0.5;
}

.error-content {
  @apply flex-1 min-w-0;
}

.error-title {
  @apply text-sm font-bold text-red-700 dark:text-red-400 mb-1;
}

.error-message {
  @apply text-sm text-red-600 dark:text-red-300;
}

.error-close {
  @apply p-1 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-100 dark:hover:bg-red-900/40 transition shrink-0;
}

.error-actions {
  @apply flex gap-2 px-4 pb-3;
}

.action-btn {
  @apply flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 dark:text-red-400 bg-white dark:bg-red-900/30 border border-red-200 dark:border-red-500/30 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/50 transition;
}

.error-details {
  @apply px-4 pb-4 space-y-3;
}

.detail-item {
  @apply space-y-1;
}

.detail-label {
  @apply block text-xs font-medium text-red-700 dark:text-red-400;
}

.detail-value {
  @apply block px-3 py-2 bg-white dark:bg-red-950/50 border border-red-200 dark:border-red-500/30 rounded-lg text-xs text-red-600 dark:text-red-300 font-mono;
}

.detail-traceback {
  @apply block px-3 py-2 bg-white dark:bg-red-950/50 border border-red-200 dark:border-red-500/30 rounded-lg text-xs text-red-600 dark:text-red-300 font-mono overflow-x-auto max-h-64 overflow-y-auto;
}

.error-footer {
  @apply px-4 pb-4;
}

.error-hint {
  @apply text-xs text-red-600 dark:text-red-400;
}
</style>
