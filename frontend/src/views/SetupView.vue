<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import type { InterviewConfig } from '../types'
import { Play, Volume2, Loader, Upload, Cpu, FileCheck, RefreshCw } from 'lucide-vue-next'
import CatLoading from '../components/CatLoading.vue'
import CustomSelect from '../components/CustomSelect.vue'
import JobTagPicker from '../components/JobTagPicker.vue'
import { ttsPreview, fetchLatestResume } from '../services/interview'
import { isReusableOcrText } from '../utils/ocr'

const router = useRouter()
const store = useInterviewStore()
const loading = computed(() => store.isSettingUp)

// ===== 配置选项定义 =====
const styleOptions = [
  { value: 'default', label: '标准模式', desc: '专业均衡，客观评估', emoji: '📘' },
  { value: 'strict', label: '高压模式', desc: '追问更深，要求更高', emoji: '🎯' },
  { value: 'friendly', label: '温和引导', desc: '更适合练习和热身', emoji: '🌤' },
  { value: 'technical_deep', label: '技术深挖', desc: '关注原理和实现细节', emoji: '🧠' },
  { value: 'behavioral', label: '行为面试', desc: '聚焦经历表达与 STAR', emoji: '🗣' },
  { value: 'system_design', label: '系统设计', desc: '考察架构设计与权衡', emoji: '🏗' },
  { value: 'rapid_fire', label: '快问快答', desc: '强调知识广度和反应速度', emoji: '⚡' },
  { value: 'project_focused', label: '项目追问', desc: '重点深挖项目细节', emoji: '📂' },
]

const typeOptions = [
  { value: 'technical', label: '技术面', desc: '代码能力与技术深度', emoji: '💻' },
  { value: 'hr', label: 'HR面', desc: '职业动机与稳定性', emoji: '🤝' },
  { value: 'manager', label: '主管面', desc: '业务理解与协作能力', emoji: '📋' },
]

const difficultyOptions = [
  { value: 'junior', label: '初级', desc: '基础概念与常见实践', emoji: '🌱' },
  { value: 'mid', label: '中级', desc: '实战经验与原理理解', emoji: '🚀' },
  { value: 'senior', label: '高级', desc: '架构能力与系统思考', emoji: '🧭' },
]
const voiceOptions = [
  { value: 4100, label: '度小雯（臻品女声）' },
  { value: 4117, label: '度小鹿（臻品女声）' },
  { value: 4115, label: '度小贤（臻品男声）' },
  { value: 4003, label: '度逍遥（臻品男声）' },
  { value: 4106, label: '度博文（新闻男声）' },
  { value: 5003, label: '度逍遥（精品男声）' },
  { value: 0, label: '度小美（基础女声）' },
  { value: 1, label: '度小宇（基础男声）' },
]

const speedOptions = [
  { label: '0.5x', spd: 2 },
  { label: '0.75x', spd: 3 },
  { label: '1x', spd: 5 },
  { label: '1.25x', spd: 7 },
  { label: '1.5x', spd: 9 },
  { label: '2x', spd: 12 },
]

const PREVIEW_TEXT = '你好，我是你的AI面试官，准备好开始面试了吗？'

const modelOptions = [
  { value: 'deepseek', label: 'DeepSeek', desc: '深度求索，代码能力强', emoji: '🧠' },
  { value: 'ernie', label: '文心一言', desc: '百度大模型，中文理解优秀', emoji: '🌐' },
  { value: 'ernie-thinking', label: '文心（深度思考）', desc: '开启思维链，回复更慢但更深入', emoji: '🔮' },
  // { value: 'deepseek-reasoner', label: 'DeepSeek R1', desc: '推理模型，逻辑分析强', emoji: '⚡' },
]

// 语音试听
const previewPlaying = ref(false)
const previewLoading = ref(false)
let previewAudioCtx: AudioContext | null = null
let previewSource: AudioBufferSourceNode | null = null

function stopPreview() {
  if (previewSource) {
    try { previewSource.stop() } catch { /* already stopped */ }
    previewSource = null
  }
  previewPlaying.value = false
}

async function playPreview() {
  if (previewPlaying.value) { stopPreview(); return }
  previewLoading.value = true
  try {
    const wavBuffer = await ttsPreview(PREVIEW_TEXT, store.config.voicePer, store.config.voiceSpd)
    if (!previewAudioCtx) previewAudioCtx = new AudioContext()
    const audioBuf = await previewAudioCtx.decodeAudioData(wavBuffer)
    stopPreview()
    previewSource = previewAudioCtx.createBufferSource()
    previewSource.buffer = audioBuf
    previewSource.connect(previewAudioCtx.destination)
    previewSource.onended = () => { previewPlaying.value = false }
    previewSource.start()
    previewPlaying.value = true
  } catch (e: any) {
    console.error('试听失败:', e)
    console.error('试听失败:', e)
    alert('语音试听失败，请确保后端已启动')
  } finally {
    previewLoading.value = false
  }
}

function setStyle(val: string) { store.config.style = val as InterviewConfig['style'] }

function buildStartInterviewErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message.trim() : String(error || '').trim()
  if (!message || message === '[object Object]') {
    return '服务连接失败，请确保 Flask 后端已启动。'
  }
  if (/Failed to fetch|NetworkError|Load failed|ERR_CONNECTION_REFUSED/i.test(message)) {
    return '服务连接失败，请确保 Flask 后端已启动。'
  }
  return `面试启动失败：${message}`
}

async function startInterview() {
  if (!store.config.jobTitle.trim()) { alert('请输入目标岗位'); return }
  try {
    await store.startInterview()
    router.push('/interview')
  } catch (e: any) {
    alert(buildStartInterviewErrorMessage(e))
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  store.config.resumeFile = input.files?.[0] || null
  // 选了新文件就清掉历史简历
  if (store.config.resumeFile) {
    store.config.resumeOcrText = undefined
    store.config.resumeFileName = undefined
  }
}

function clearHistoryResume() {
  store.config.resumeOcrText = undefined
  store.config.resumeFileName = undefined
}

// 进入配置页时，自动加载用户最近的简历（如果当前没有已加载的简历）
onMounted(async () => {
  if (store.config.resumeFile || store.config.resumeOcrText) return
  try {
    const resume = await fetchLatestResume()
    const latestOcrText = resume?.ocr_result || ''
    if (isReusableOcrText(latestOcrText)) {
      store.config.resumeOcrText = latestOcrText
      store.config.resumeFileName = resume?.file_name || '历史简历'
    }
  } catch { /* 静默 */ }
})
</script>

<template>
  <div class="fade-in min-h-full max-w-4xl mx-auto">
    <CatLoading
      v-if="loading"
      variant="corner"
      message="AI 面试官正在准备中"
      :stage="store.thinkingStage"
      :thinking-text="store.thinkingText"
    />

    <div class="mb-6">
      <h2 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl dark:text-white">配置专属面试房间</h2>
      <p class="mt-2 text-sm font-medium text-slate-500 dark:text-slate-400">设定岗位与风格，AI 将实时解析简历生成攻击策略</p>
    </div>

    <div
      v-if="false && loading"
      class="mb-6 rounded-3xl border border-indigo-200 bg-white/90 p-5 shadow-lg shadow-indigo-100/60 backdrop-blur dark:border-indigo-500/20 dark:bg-slate-950/80 dark:shadow-transparent"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div class="min-w-0">
          <div class="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-white">
            <Loader class="h-4 w-4 animate-spin text-primary" />
            AI 面试官正在准备中
          </div>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            初始化过程已经改成局部加载，你仍然可以继续查看和调整表单；如果想切换配置，可以直接取消本次初始化。          </p>
          <p v-if="store.thinkingStage" class="mt-3 text-xs font-medium text-primary">{{ store.thinkingStage }}</p>
        </div>
        <button
          type="button"
          @click="store.cancelSetup"
          class="inline-flex shrink-0 items-center justify-center rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-red-300 hover:text-red-500 dark:border-white/10 dark:text-slate-300 dark:hover:border-red-500/30 dark:hover:text-red-400"
        >
          取消初始化        </button>
      </div>

      <div
        v-if="store.thinkingText"
        class="mt-4 max-h-48 overflow-y-auto rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-600 dark:bg-white/5 dark:text-slate-300"
      >
        {{ store.thinkingText }}
      </div>
    </div>

    <form @submit.prevent="startInterview" class="space-y-5">

      <!-- 第一行：大模型 + 简历 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="config-card">
          <label class="config-label"><Cpu class="w-3.5 h-3.5 inline -mt-0.5" /> AI 大模型</label>
          <div class="flex gap-2">
            <button v-for="m in modelOptions" :key="m.value" type="button"
              @click="store.config.modelProvider = m.value"
              class="chip-btn" :class="store.config.modelProvider === m.value ? 'chip-active' : 'chip-idle'">
              <span>{{ m.emoji }}</span> {{ m.label }}
            </button>
          </div>
          <p class="text-helper mt-1">{{ modelOptions.find(m => m.value === store.config.modelProvider)?.desc }}</p>
        </div>
        <div class="config-card">
          <label class="config-label">
            <Upload class="w-3.5 h-3.5 inline -mt-0.5" /> 上传简历
            <span class="text-helper font-normal ml-1">PDF / Word(.docx) / Markdown / TXT / 图片</span>
          </label>
          <!-- 已加载历史简历 -->
          <div v-if="store.config.resumeOcrText && !store.config.resumeFile" class="flex items-center gap-3">
            <div class="flex-1 min-w-0 flex items-center gap-2 px-3 py-2.5 rounded-xl bg-green-50 dark:bg-green-900/15 border border-green-200 dark:border-green-500/20">
              <FileCheck class="w-4 h-4 text-green-600 dark:text-green-400 shrink-0" />
              <span class="text-sm text-green-700 dark:text-green-400 truncate">已加载: {{ store.config.resumeFileName || '历史简历' }}</span>
            </div>
            <button type="button" @click="clearHistoryResume"
              class="shrink-0 inline-flex items-center gap-1.5 px-3 py-2.5 rounded-xl border text-xs font-medium transition-all border-slate-200 dark:border-white/10 text-slate-500 dark:text-white/50 hover:border-primary hover:text-primary whitespace-nowrap">
              <RefreshCw class="w-3.5 h-3.5" /> 重新上传
            </button>
          </div>
          <!-- 正常文件上传 -->
          <input v-else type="file" accept=".pdf,.docx,.md,.markdown,.txt,.png,.jpg,.jpeg,.bmp,.webp,.heic,.heif" @change="onFileChange"
            class="w-full text-sm file:mr-3 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 cursor-pointer" />
        </div>
      </div>

      <!-- 目标岗位（独占一行，标签默认展开） -->
      <div class="config-card">
        <label class="config-label">目标岗位</label>
        <JobTagPicker v-model="store.config.jobTitle" :default-expanded="true" />
      </div>

      <div class="config-card">
        <label class="config-label">岗位要求 / 职位描述（可选）</label>
        <textarea
          v-model="store.config.jobRequirements"
          class="config-input min-h-[140px] resize-y"
          placeholder="可粘贴岗位职责、技术栈要求、年限要求、加分项等。AI 会把这部分作为考察重点和评分基准，不会当成候选人已经具备的经历。"
        />
        <p class="text-helper mt-2">建议直接粘贴 JD 原文，尤其是核心职责、必备技能、经验年限和加分项。</p>
      </div>

      <!-- 第二行：面试轮次 + 难度 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="config-card">
          <label class="config-label">面试轮次</label>
          <div class="flex gap-2">
            <button v-for="t in typeOptions" :key="t.value" type="button"
              @click="store.config.interviewType = t.value"
              class="chip-btn" :class="store.config.interviewType === t.value ? 'chip-active' : 'chip-idle'">
              <span>{{ t.emoji }}</span> {{ t.label }}
            </button>
          </div>
          <p class="text-helper mt-1">{{ typeOptions.find(t => t.value === store.config.interviewType)?.desc }}</p>
        </div>
        <div class="config-card">
          <label class="config-label">难度级别</label>
          <div class="flex gap-2">
            <button v-for="d in difficultyOptions" :key="d.value" type="button"
              @click="store.config.difficulty = d.value"
              class="chip-btn" :class="store.config.difficulty === d.value ? 'chip-active' : 'chip-idle'">
              <span>{{ d.emoji }}</span> {{ d.label }}
            </button>
          </div>
          <p class="text-helper mt-1">{{ difficultyOptions.find(d => d.value === store.config.difficulty)?.desc }}</p>
        </div>
      </div>

      <!-- 第三行：面试风格（卡片网格） -->
      <div class="config-card">
        <label class="config-label">面试风格</label>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <button v-for="s in styleOptions" :key="s.value" type="button"
            @click="setStyle(s.value)"
            class="style-card-btn"
            :class="store.config.style === s.value ? 'style-card-active' : 'style-card-idle'">
            <div class="text-lg mb-1">{{ s.emoji }}</div>
            <div class="style-card-title">{{ s.label }}</div>
            <div class="style-card-desc">{{ s.desc }}</div>
          </button>
        </div>
      </div>

      <!-- 第四行：功能开关 -->
      <div class="config-card">
        <label class="config-label">训练功能</label>
        <div class="flex flex-wrap gap-4">
          <label class="inline-flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" v-model="store.config.featureDeep"
              class="w-4 h-4 rounded border-slate-300 text-primary focus:ring-2 focus:ring-indigo-500/30" />
            <span class="text-secondary-label">🔍 简历压力深挖</span>
            <span class="text-helper">连环追问，识别注水</span>
          </label>
          <label class="inline-flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" v-model="store.config.featureVad"
              class="w-4 h-4 rounded border-slate-300 text-primary focus:ring-2 focus:ring-indigo-500/30" />
            <span class="text-secondary-label">🆘 柔性防卡壳</span>
            <span class="text-helper">卡壳时给予提示引导</span>
          </label>
        </div>
      </div>

      <!-- 第五行：语音设置 -->
      <div class="config-card">
        <label class="config-label"><Volume2 class="w-3.5 h-3.5 inline -mt-0.5" /> AI 面试官语音</label>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span class="text-helper block mb-1.5">音色</span>
            <CustomSelect
              v-model="store.config.voicePer"
              :options="voiceOptions"
              placeholder="选择音色"
            />
          </div>
          <div>
            <span class="text-helper block mb-1.5">语速</span>
            <div class="flex gap-1.5 flex-wrap">
              <button v-for="s in speedOptions" :key="s.spd" type="button" @click="store.config.voiceSpd = s.spd"
                class="chip-btn text-xs" :class="store.config.voiceSpd === s.spd ? 'chip-active' : 'chip-idle'">
                {{ s.label }}
              </button>
            </div>
          </div>
        </div>
        <button type="button" @click="playPreview" :disabled="previewLoading"
          class="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all disabled:opacity-50 border"
          :class="previewPlaying
            ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-500/30'
            : 'bg-indigo-50 dark:bg-primary/5 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-500/30 hover:bg-indigo-100 dark:hover:bg-primary/10 dark:hover:border-indigo-400/50'">
          <Loader v-if="previewLoading" class="w-4 h-4 animate-spin" />
          <Volume2 v-else class="w-4 h-4" />
          {{ previewLoading ? '加载中...' : previewPlaying ? '停止试听' : '试听当前语音' }}
        </button>
      </div>

      <!-- 开始按钮 -->
      <button type="submit" :disabled="loading"
        class="w-full bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 dark:bg-primary dark:hover:bg-indigo-700">
        <Play class="w-5 h-5" />
        <span>{{ loading ? '系统初始化中...' : '开始沉浸式面试' }}</span>
      </button>
      <button
        v-if="loading"
        type="button"
        @click="store.cancelSetup"
        class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-600 transition hover:border-rose-300 hover:text-rose-500 dark:border-white/10 dark:text-slate-300 dark:hover:border-rose-500/30 dark:hover:text-rose-400"
      >
        取消当前初始化      </button>
    </form>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

/* 暗黑模式色彩规范 */
.dark {
  --bg-elevated-1: #1A1A24;
  --bg-elevated-0: #0F0F15;
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.65);
  --text-tertiary: rgba(255, 255, 255, 0.4);
  --border-default: rgba(255, 255, 255, 0.1);
  --border-hover: rgba(255, 255, 255, 0.2);
}

.config-card {
  @apply p-5 rounded-2xl border transition-colors;
  /* 亮色模式 */
  background: rgba(255, 255, 255, 0.7);
  border-color: rgb(226, 232, 240);
}
.dark .config-card {
  /* 暗色模式：深色卡片背景 */
  background: var(--bg-elevated-1);
  border-color: var(--border-default);
}

.config-label {
  @apply block text-sm font-bold mb-3;
  color: rgb(51, 65, 85);
}
.dark .config-label {
  color: var(--text-primary);
}

.config-input {
  @apply w-full px-4 py-3 rounded-xl border outline-none transition-all;
  background: transparent;
  border-color: rgb(203, 213, 225);
  color: rgb(15, 23, 42);
}
.dark .config-input {
  /* 暗色模式：输入框背景比卡片更深 */
  background: var(--bg-elevated-0);
  border-color: var(--border-default);
  color: var(--text-primary);
}
.config-input::placeholder {
  color: rgb(148, 163, 184);
}
.dark .config-input::placeholder {
  color: var(--text-tertiary);
}
.config-input:focus {
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 30%, transparent);
}
.dark .config-input:focus {
  border-color: var(--border-hover);
}

.chip-btn {
  @apply px-3 py-2 rounded-xl border text-sm font-medium transition-all inline-flex items-center gap-1.5;
}
.chip-active {
  @apply shadow-sm;
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 15%, transparent);
  color: var(--color-primary);
}
.chip-idle {
  border-color: rgb(226, 232, 240);
  color: rgb(71, 85, 105);
  background: transparent;
}
.chip-idle:hover {
  background: rgb(248, 250, 252);
}
.dark .chip-idle {
  border-color: var(--border-default);
  color: var(--text-secondary);
  background: transparent;
}
.dark .chip-idle:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-hover);
}

/* 椋庢牸鍗＄墖鎸夐挳 */
.style-card-btn {
  @apply p-3 rounded-xl border text-left transition-all;
}
.style-card-active {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 5%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--color-primary) 30%, transparent);
}
.style-card-idle {
  border-color: rgb(226, 232, 240);
  background: transparent;
}
.style-card-idle:hover {
  border-color: rgb(203, 213, 225);
  background: rgb(248, 250, 252);
}
.dark .style-card-idle {
  border-color: var(--border-default);
  background: transparent;
}
.dark .style-card-idle:hover {
  border-color: var(--border-hover);
  background: rgba(255, 255, 255, 0.03);
}
.style-card-title {
  @apply text-sm font-bold;
  color: rgb(51, 65, 85);
}
.dark .style-card-title {
  color: var(--text-primary);
}
.style-card-desc {
  @apply text-xs mt-0.5;
  color: rgb(148, 163, 184);
}
.dark .style-card-desc {
  color: var(--text-tertiary);
}

/* 杈呭姪鏂囧瓧 */
.text-helper {
  @apply text-xs;
  color: rgb(148, 163, 184);
}
.dark .text-helper {
  color: var(--text-tertiary);
}

.text-secondary-label {
  @apply text-sm;
  color: rgb(71, 85, 105);
}
.dark .text-secondary-label {
  color: var(--text-secondary);
}

/* 鏂囦欢涓婁紶 */
input[type="file"] {
  color: rgb(100, 116, 139);
}
.dark input[type="file"] {
  color: var(--text-secondary);
}

select.config-input {
  @apply dark:[&>option]:bg-slate-900;
}
</style>
