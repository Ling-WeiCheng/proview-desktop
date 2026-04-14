<script setup lang="ts">
import { Bot, Mic, PhoneOff, BrainCircuit, AudioLines, Pencil, Sparkles, MessageCircle } from 'lucide-vue-next'
import { useInterviewStore } from '../stores/interview'
import { useTimer } from '../composables/useTimer'
import { computed, watch, nextTick, ref } from 'vue'

const store = useInterviewStore()
const { formatted, start, stop } = useTimer()
const panelEl = ref<HTMLElement | null>(null)

const emit = defineEmits<{ 'end-interview': [] }>()

const isThinking = computed(() => store.aiState === 'thinking')
const hasPipeline = computed(() => store.pipeline.length > 0 || !!store.thinkingText)

const statusText = computed(() => {
  switch (store.aiState) {
    case 'speaking': return '面试官讲话中...'
    case 'thinking': return store.thinkingStage || '面试官正在深度思考...'
    default: return '等待您的回答'
  }
})

const stepIcon = (type: string) => {
  switch (type) {
    case 'recording': return AudioLines
    case 'stt': return AudioLines
    case 'input': return Pencil
    case 'polish': return Sparkles
    case 'response': return MessageCircle
    default: return BrainCircuit
  }
}

const stepColor = (type: string) => {
  switch (type) {
    case 'recording': return 'text-red-400'
    case 'stt': return 'text-amber-400'
    case 'input': return 'text-blue-400'
    case 'polish': return 'text-green-400'
    case 'response': return 'text-purple-400'
    default: return 'text-indigo-400'
  }
}

// 自动滚动到底部
watch([() => store.thinkingText, () => store.pipeline.length], () => {
  nextTick(() => {
    if (panelEl.value) {
      panelEl.value.scrollTop = panelEl.value.scrollHeight
    }
  })
})

defineExpose({ startTimer: start, stopTimer: stop })
</script>

<template>
  <div class="w-full md:w-5/12 flex flex-col min-h-0 bg-slate-900 dark:bg-black rounded-3xl overflow-hidden relative shadow-inner border border-slate-800">
    <!-- 顶部状态栏 -->
    <div class="p-4 flex justify-between items-center shrink-0 border-b border-white/5">
      <div class="flex items-center gap-2 text-red-500">
        <span class="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
        <span class="text-xs font-bold tracking-widest">REC</span>
      </div>
      <div class="text-sm font-mono bg-black/50 text-white px-3 py-1 rounded-md border border-white/20">{{ formatted }}</div>
    </div>

    <!-- 主体区域 -->
    <div class="flex-1 flex flex-col min-h-0">
      <!-- 头像 + 状态（紧凑） -->
      <div class="flex items-center gap-3 px-4 py-3 shrink-0">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 p-0.5 shrink-0 transition-all"
             :class="{ 'ai-thinking-glow': isThinking }">
          <div class="w-full h-full bg-slate-900 rounded-full flex items-center justify-center text-lg text-white">
            <Bot />
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-white/90 text-sm font-medium">AI 面试官</p>
          <p class="text-indigo-300/70 text-xs flex items-center gap-1">
            <BrainCircuit v-if="isThinking" class="w-3 h-3 animate-pulse" />
            {{ statusText }}
          </p>
        </div>
      </div>

      <!-- 处理链路面板 -->
      <div ref="panelEl" class="flex-1 min-h-0 overflow-y-auto px-4 pb-3 pipeline-scroll">
        <!-- 空状态 -->
        <div v-if="!hasPipeline" class="h-full flex flex-col items-center justify-center opacity-30">
          <div class="w-32 h-32 border border-primary/50 rounded-full flex items-center justify-center animate-pulse">
            <Bot class="w-12 h-12 text-primary/50" />
          </div>
          <p class="text-white/30 text-xs mt-4">发送消息后，处理链路将在此展示</p>
        </div>

        <!-- 链路步骤 -->
        <div v-if="hasPipeline" class="space-y-2">
          <div v-for="(step, i) in store.pipeline" :key="i" class="pipeline-step fade-in">
            <div class="flex items-start gap-2">
              <div class="w-5 h-5 rounded-md flex items-center justify-center shrink-0 mt-0.5"
                   :class="stepColor(step.type)" style="background: rgba(255,255,255,0.05);">
                <component :is="stepIcon(step.type)" class="w-3 h-3" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="step-label" :class="stepColor(step.type)">{{ step.label }}</p>
                <p class="step-content">{{ step.content }}</p>
              </div>
            </div>
          </div>

          <!-- LLM 思维链（实时流式） -->
          <div v-if="isThinking && store.thinkingText" class="pipeline-step thinking-step fade-in">
            <div class="flex items-start gap-2">
              <div class="w-5 h-5 rounded-md flex items-center justify-center shrink-0 mt-0.5 text-indigo-400"
                   style="background: rgba(255,255,255,0.05);">
                <BrainCircuit class="w-3 h-3" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="step-label text-indigo-400">
                  LLM 思维链
                  <span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span>
                </p>
                <p class="step-content thinking-stream">{{ store.thinkingText }}</p>
              </div>
            </div>
          </div>

          <!-- 评估状态指示器 -->
          <div v-if="store.evalInProgress" class="pipeline-step eval-indicator fade-in">
            <div class="flex items-start gap-2">
              <div class="w-5 h-5 rounded-md flex items-center justify-center shrink-0 mt-0.5 text-emerald-400"
                   style="background: rgba(255,255,255,0.05);">
                <BrainCircuit class="w-3 h-3 animate-pulse" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="step-label text-emerald-400">
                  AI 正在分析本轮表现
                  <span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span>
                </p>
                <p class="step-content">
                  第 {{ store.currentEvalTurn }} 轮评估中...
                </p>
              </div>
            </div>
          </div>

          <!-- 评估草稿卡片 -->
          <div v-for="(draft, i) in store.evalDrafts" :key="i" class="pipeline-step eval-draft fade-in">
            <div class="flex items-start gap-2">
              <div class="w-5 h-5 rounded-md flex items-center justify-center shrink-0 mt-0.5 text-amber-400"
                   :class="{ 'animate-pulse': !draft.completed }"
                   style="background: rgba(255,255,255,0.05);">
                <BrainCircuit class="w-3 h-3" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="step-label text-amber-400">
                  第 {{ draft.turn }} 轮评估
                  <span v-if="!draft.completed" class="text-xs opacity-70">(分析中...)</span>
                  <span v-else class="text-xs opacity-70">✓</span>
                </p>
                <div class="space-y-1 mt-1">
                  <p v-if="draft.strength" class="step-content text-green-300">
                    <span class="font-bold">✨ 亮点:</span> {{ draft.strength }}
                  </p>
                  <p v-if="draft.weakness" class="step-content text-red-300">
                    <span class="font-bold">⚠️ 不足:</span> {{ draft.weakness }}
                  </p>
                  <p v-if="draft.note" class="step-content text-blue-300">
                    <span class="font-bold">📝 备注:</span> {{ draft.note }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部控制 -->
    <div class="bg-black/80 p-4 flex justify-center items-center gap-6 border-t border-white/10 shrink-0">
      <button class="w-11 h-11 rounded-full bg-slate-800 text-white flex items-center justify-center hover:bg-slate-700 transition-colors">
        <Mic class="w-5 h-5" />
      </button>
      <button @click="emit('end-interview')"
              class="px-5 h-11 rounded-full bg-red-500 hover:bg-red-600 text-white font-bold flex items-center justify-center gap-2 transition-colors text-sm">
        <PhoneOff class="w-4 h-4" /> 结束面试
      </button>
    </div>
  </div>
</template>

<style scoped>
.pipeline-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.15) transparent;
}
.pipeline-step {
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.thinking-step {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(139, 92, 246, 0.04));
  border-color: rgba(99, 102, 241, 0.12);
}
.eval-indicator {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.06), rgba(5, 150, 105, 0.04));
  border-color: rgba(16, 185, 129, 0.12);
}
.eval-draft {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.06), rgba(217, 119, 6, 0.04));
  border-color: rgba(245, 158, 11, 0.12);
}
.step-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 3px;
}
.step-content {
  font-size: 12px;
  line-height: 1.6;
  color: rgba(226, 232, 240, 0.7);
  white-space: pre-wrap;
  word-break: break-all;
}
.thinking-stream {
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 11px;
  color: rgba(165, 180, 252, 0.65);
}
.thinking-dots span {
  animation: dot-blink 1.4s infinite;
  opacity: 0;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-blink {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}
.ai-thinking-glow {
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.3), 0 0 30px rgba(139, 92, 246, 0.15);
  animation: thinking-pulse 2s ease-in-out infinite;
}
@keyframes thinking-pulse {
  0%, 100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.3), 0 0 30px rgba(139, 92, 246, 0.15); }
  50% { box-shadow: 0 0 25px rgba(99, 102, 241, 0.5), 0 0 50px rgba(139, 92, 246, 0.25); }
}
.fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
