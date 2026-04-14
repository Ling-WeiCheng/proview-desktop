<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  Building2,
  ClipboardList,
  Flame,
  Heart,
  Loader,
  MessageSquare,
  Mic,
  MicOff,
  Microscope,
  Send,
  Square,
  Target,
  Volume2,
  VolumeX,
  Users,
  Zap,
} from 'lucide-vue-next'
import { useInterviewStore } from '../stores/interview'
import { polishSpeechText } from '../services/interview'
import ChatMessage from './ChatMessage.vue'
import SystemMessage from './SystemMessage.vue'
import { useVoice } from '../composables/useVoice'

const store = useInterviewStore()
const userInput = ref('')
const chatBox = ref<HTMLElement | null>(null)
const inputMode = ref<'text' | 'voice'>('voice')
const isVoiceInput = ref(false)
const isAwaitingMicPermission = ref(false)
const isPinnedToBottom = ref(true)
const autoSpokenOpeningMessageId = ref<number | null>(null)
const defaultSpeechHint = '点击开始录音'
const speechHint = ref(defaultSpeechHint)

const {
  isRecording,
  isPlaying,
  sttLoading,
  ensureMicrophonePermission,
  startRecording,
  stopRecordingAndRecognize,
  playTTS,
  stopPlayback,
} = useVoice()

const voiceEnabled = ref(true)
const isResponding = computed(() => store.isResponding)

const statusBadge = computed(() => {
  if (store.responseStatus === 'stopping') {
    return { text: '正在停止生成', cls: 'bg-rose-100 dark:bg-rose-900/40 text-rose-600 dark:text-rose-300' }
  }
  switch (store.aiState) {
    case 'speaking':
      return { text: 'AI 回答中', cls: 'bg-indigo-100 dark:bg-indigo-900/50 text-primary dark:text-indigo-300' }
    case 'thinking':
      return { text: '深度分析中', cls: 'bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400' }
    default:
      return { text: '等待作答', cls: 'bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400' }
  }
})

const modeBadge = computed(() => {
  const defaultBadge = { label: '标准模式', icon: Target, cls: 'text-blue-600 dark:text-blue-400' }
  const map: Record<string, typeof defaultBadge> = {
    default: defaultBadge,
    strict: { label: '高压模式', icon: Flame, cls: 'text-red-600 dark:text-red-400' },
    friendly: { label: '温和模式', icon: Heart, cls: 'text-emerald-600 dark:text-emerald-400' },
    technical_deep: { label: '技术深挖', icon: Microscope, cls: 'text-violet-600 dark:text-violet-400' },
    behavioral: { label: '行为面试', icon: Users, cls: 'text-cyan-600 dark:text-cyan-400' },
    system_design: { label: '系统设计', icon: Building2, cls: 'text-orange-600 dark:text-orange-400' },
    rapid_fire: { label: '快问快答', icon: Zap, cls: 'text-yellow-600 dark:text-yellow-400' },
    project_focused: { label: '项目深挖', icon: ClipboardList, cls: 'text-pink-600 dark:text-pink-400' },
  }
  return map[store.config.style] ?? defaultBadge
})

const canStartVoiceRecording = computed(() =>
  inputMode.value === 'voice'
  && !isResponding.value
  && !sttLoading.value
  && !isAwaitingMicPermission.value
  && !isRecording.value
)

const voiceModeLabel = computed(() => {
  if (isAwaitingMicPermission.value) return '等待麦克风授权...'
  if (sttLoading.value) return '正在识别语音...'
  if (isRecording.value) return '录音中，点击结束'
  if (isResponding.value) return '请先停止当前生成'
  return '点击开始录音'
})

const lastMessageContent = computed(() => {
  const lastMessage = store.messages[store.messages.length - 1]
  return lastMessage?.content || ''
})

const latestAiMessage = computed(() =>
  [...store.messages].reverse().find((message) => message.role === 'ai')
)

const hasUserMessage = computed(() =>
  store.messages.some((message) => message.role === 'user')
)

function resetVoiceState(nextHint = defaultSpeechHint) {
  isAwaitingMicPermission.value = false
  speechHint.value = nextHint
}

function updatePinnedState() {
  const el = chatBox.value
  if (!el) return
  const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
  isPinnedToBottom.value = distanceFromBottom < 96
}

function scrollToBottom(force = false) {
  nextTick(() => {
    const el = chatBox.value
    if (!el) return
    if (!force && !isPinnedToBottom.value) return
    el.scrollTop = el.scrollHeight
  })
}

async function stopGeneration() {
  stopPlayback()
  await store.stopResponseGeneration()
}

function speakMessage(content: string) {
  store.setAiState('speaking')
  playTTS(content, store.config.voicePer, store.config.voiceSpd).catch((error) => {
    console.warn('TTS playback failed:', error)
    store.setAiState('idle')
  })
}

function tryAutoSpeakOpeningMessage() {
  const message = latestAiMessage.value
  if (!message || !message.content.trim()) return
  if (hasUserMessage.value) return
  if (!voiceEnabled.value || isPlaying.value || store.isResponding) return
  if (autoSpokenOpeningMessageId.value === message.id) return

  autoSpokenOpeningMessageId.value = message.id
  speakMessage(message.content)
}

watch(isPlaying, (value) => {
  if (!value && !store.isResponding) store.setAiState('idle')
})

watch(
  () => [latestAiMessage.value?.id ?? null, hasUserMessage.value, voiceEnabled.value, store.isResponding] as const,
  () => {
    tryAutoSpeakOpeningMessage()
  },
  { flush: 'post' }
)

async function finalizeVoiceInput() {
  try {
    speechHint.value = '正在识别语音...'
    const text = await stopRecordingAndRecognize()
    if (!text) return

    userInput.value = text
    isVoiceInput.value = true
    store.addPipelineStep('stt', '语音识别原文', text)
    await sendMessage()
  } catch (error: any) {
    console.error('语音识别失败:', error)
    alert('语音识别失败: ' + (error.message || error))
  } finally {
    resetVoiceState()
  }
}

async function beginVoiceRecording() {
  if (!canStartVoiceRecording.value) return

  try {
    isAwaitingMicPermission.value = true
    speechHint.value = '正在请求麦克风权限...'
    const permissionResult = await ensureMicrophonePermission()
    isAwaitingMicPermission.value = false

    store.clearPipeline()
    if (permissionResult === 'granted_after_prompt') {
      store.addPipelineStep('permission', '麦克风权限已授权', '已获取权限，开始录音')
    }
    speechHint.value = '录音中，点击按钮结束并发送...'
    store.addPipelineStep('recording', '正在录音', '等待用户语音输入...')
    await startRecording()
  } catch {
    resetVoiceState()
    alert('无法访问麦克风，请检查浏览器权限')
  }
}

async function endVoiceRecording() {
  if (!isRecording.value) return
  await finalizeVoiceInput()
}

function toggleVoiceRecording() {
  if (isRecording.value) {
    void endVoiceRecording()
    return
  }

  void beginVoiceRecording()
}

function handleWindowBlur() {
  if (!isRecording.value) return
  void endVoiceRecording()
}

function toggleInputMode() {
  inputMode.value = inputMode.value === 'text' ? 'voice' : 'text'
  if (inputMode.value === 'text') {
    if (isRecording.value) {
      void endVoiceRecording()
    } else {
      resetVoiceState()
    }
  } else {
    userInput.value = ''
  }
}

async function sendMessage() {
  if (store.isResponding) return
  if (!userInput.value.trim()) return

  const text = userInput.value.trim()
  const fromVoice = isVoiceInput.value
  isVoiceInput.value = false
  userInput.value = ''

  if (!fromVoice) {
    store.clearPipeline()
    store.addPipelineStep('input', '用户输入', text)
  }

  scrollToBottom(true)

  try {
    const { response, msgId, interrupted } = await store.sendUserMessage(text)

    if (fromVoice && msgId) {
      void polishSpeechText(text)
        .then(({ text: polished, corrections }) => {
          if (corrections.length > 0) {
            store.updateMessage(msgId, polished, corrections)
            const correctionDesc = corrections.map((item) => `“${item.original}”→“${item.corrected}”`).join('、')
            store.addPipelineStep('polish', '语音清洗纠正', correctionDesc)
          } else {
            store.addPipelineStep('polish', '语音清洗', '未发现需要纠正的术语')
          }
        })
        .catch(() => {
          store.addPipelineStep('polish', '语音清洗', '语音清洗请求失败，已跳过')
        })
    }

    if (response) {
      store.addPipelineStep('response', '面试官回复', response.slice(0, 200) + (response.length > 200 ? '...' : ''))
      if (!interrupted && voiceEnabled.value) {
        speakMessage(response)
      }
    }
  } catch {
    // Errors are already handled in the store.
  }
}

function onKeypress(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (!store.isResponding) void sendMessage()
  }
}

watch(() => store.messages.length, () => scrollToBottom(true))
watch(lastMessageContent, () => scrollToBottom())

onMounted(() => {
  window.addEventListener('blur', handleWindowBlur)
  nextTick(() => updatePinnedState())
  nextTick(() => tryAutoSpeakOpeningMessage())
})

onBeforeUnmount(() => {
  window.removeEventListener('blur', handleWindowBlur)
})

defineExpose({
  stopVoicePlayback: stopPlayback,
})
</script>

<template>
  <div class="flex min-h-0 w-full flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white dark:border-white/5 dark:bg-[#0A0A0F]/50 md:w-7/12">
    <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 p-4 dark:border-white/5 dark:bg-transparent">
      <div class="min-w-0">
        <h3 class="flex items-center gap-2 font-bold text-slate-800 dark:text-white">
          <MessageSquare class="h-4 w-4 text-primary" /> 实时互动
          <span class="ml-2 flex items-center gap-1 text-xs font-medium" :class="modeBadge.cls">
            <component :is="modeBadge.icon" class="h-3 w-3" />
            {{ modeBadge.label }}
          </span>
        </h3>
      </div>

      <div class="flex items-center gap-2">
        <button
          v-if="store.canStopResponse"
          type="button"
          @click="stopGeneration"
          class="inline-flex items-center gap-1 rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-600 transition hover:bg-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:hover:bg-rose-900/50"
        >
          <Square class="h-3 w-3 fill-current" />
          停止生成
        </button>
        <span class="rounded-full px-3 py-1 text-xs font-medium" :class="statusBadge.cls">
          {{ statusBadge.text }}
        </span>
        <button
          @click="voiceEnabled = !voiceEnabled; if (!voiceEnabled) stopPlayback()"
          class="rounded-lg p-1.5 transition-colors"
          :class="voiceEnabled ? 'bg-indigo-50 text-primary dark:bg-indigo-900/30' : 'text-slate-400 dark:text-slate-600'"
          :title="voiceEnabled ? '关闭语音朗读' : '开启语音朗读'"
        >
          <Volume2 v-if="voiceEnabled" class="h-4 w-4" />
          <VolumeX v-else class="h-4 w-4" />
        </button>
      </div>
    </div>

    <div
      ref="chatBox"
      class="custom-scroll flex-1 space-y-6 overflow-y-auto p-6"
      @scroll="updatePinnedState"
    >
      <template v-for="msg in store.messages" :key="msg.id">
        <SystemMessage v-if="msg.role === 'system'" :text="msg.content" />
        <ChatMessage v-else :role="msg.role" :content="msg.content" :corrections="msg.corrections" />
      </template>
    </div>

    <div class="shrink-0 border-t border-slate-100 bg-white p-4 dark:border-white/5 dark:bg-transparent">
      <div class="mb-3 flex items-center justify-between gap-3">
        <div class="text-xs text-slate-500 dark:text-slate-400">
          {{ inputMode === 'text' ? '当前为文本输入模式' : '当前为语音输入模式' }}
        </div>
        <button
          type="button"
          @click="toggleInputMode"
          class="inline-flex h-11 w-11 items-center justify-center rounded-xl transition-all"
          :class="inputMode === 'voice'
            ? 'bg-primary text-white shadow-md shadow-indigo-500/25'
            : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700'"
          :title="inputMode === 'voice' ? '切换到文本模式' : '切换到语音输入模式'"
        >
          <Mic v-if="inputMode === 'text'" class="h-5 w-5" />
          <Send v-else class="h-5 w-5" />
        </button>
      </div>

      <div
        v-if="store.isResponding"
        class="mb-3 flex items-start gap-2 rounded-2xl border border-indigo-100 bg-indigo-50/80 px-3 py-2 text-sm text-indigo-700 dark:border-indigo-500/20 dark:bg-indigo-500/10 dark:text-indigo-200"
      >
        <Loader class="mt-0.5 h-4 w-4 shrink-0 animate-spin" />
        <div>
          <p class="font-medium">{{ store.thinkingStage || '面试官正在思考...' }}</p>
          <p class="mt-1 text-xs text-indigo-600/80 dark:text-indigo-200/80">
            你现在仍然可以滚动查看历史消息、继续输入下一个问题，或者点击“停止生成”。
          </p>
        </div>
      </div>

      <div
        v-if="inputMode === 'voice' && (isRecording || sttLoading || isAwaitingMicPermission)"
        class="mb-3 flex items-center gap-2 px-2 text-sm"
        :class="isRecording ? 'animate-pulse text-red-500' : 'text-amber-500'"
      >
        <span
          class="h-2 w-2 rounded-full"
          :class="isRecording ? 'bg-red-500' : 'bg-amber-500'"
        ></span>
        {{ speechHint }}
      </div>

      <div v-if="sttLoading && inputMode === 'text'" class="mb-3 flex items-center gap-2 px-2 text-sm text-amber-500">
        <Loader class="h-4 w-4 animate-spin" /> 语音识别中...
      </div>

      <div class="relative flex gap-3">
        <template v-if="inputMode === 'text'">
          <textarea
            v-model="userInput"
            @keypress="onKeypress"
            rows="2"
            class="flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition-colors focus:ring-1 focus:ring-indigo-500 dark:border-white/10 dark:bg-slate-900 dark:text-white"
            placeholder="输入回答，或先写下你的下一个问题..."
          />
          <button
            v-if="!store.isResponding"
            @click="sendMessage"
            :disabled="!userInput.trim()"
            class="self-end flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-white transition-all hover:bg-indigo-700 disabled:opacity-50"
          >
            <Send class="h-5 w-5" />
          </button>
          <button
            v-else
            type="button"
            @click="stopGeneration"
            class="self-end flex h-12 w-12 items-center justify-center rounded-xl bg-rose-500 text-white transition-all hover:bg-rose-600"
            title="停止生成"
          >
            <Square class="h-4 w-4 fill-current" />
          </button>
        </template>

        <button
          v-else
          type="button"
          :disabled="!canStartVoiceRecording && !isRecording"
          class="w-full select-none rounded-2xl px-5 py-4 text-left transition-all disabled:opacity-50"
          :class="isRecording
            ? 'bg-red-500 text-white shadow-lg shadow-red-500/25 ring-2 ring-red-300 dark:ring-red-800'
            : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700'"
          @click="toggleVoiceRecording"
        >
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <div
                class="flex h-11 w-11 items-center justify-center rounded-2xl"
                :class="isRecording ? 'bg-white/20' : 'bg-white dark:bg-slate-900/70'"
              >
                <MicOff v-if="isRecording" class="h-5 w-5" />
                <Mic v-else class="h-5 w-5 text-primary dark:text-indigo-300" />
              </div>
              <div>
                <div class="text-base font-semibold">{{ voiceModeLabel }}</div>
                <div class="text-xs opacity-80">
                  {{ isRecording ? '再次点击后自动识别并发送' : '点击开始录音，再次点击结束并发送' }}
                </div>
              </div>
            </div>
            <div
              class="rounded-full px-3 py-1 text-xs font-medium"
              :class="isRecording ? 'bg-white/20 text-white' : 'bg-white text-slate-500 dark:bg-slate-900/70 dark:text-slate-300'"
            >
              {{ isRecording ? '点击结束' : '点击开始' }}
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
