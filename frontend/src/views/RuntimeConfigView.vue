<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, RefreshCw, Settings } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import {
  describeRuntimeApiBaseUrl,
  fetchRuntimeConfig,
  getRuntimeApiBaseUrl,
  probeApiHealth,
  saveRuntimeConfig,
  setRuntimeApiBaseUrl,
  type RuntimeConfigResponse,
} from '../services/runtimeConfig'

type RuntimeFormKey =
  | 'apiBaseUrl'
  | 'LOCAL_USER_NAME'
  | 'DEEPSEEK_BASE_URL'
  | 'DEEPSEEK_API_KEY'
  | 'ERNIE_BASE_URL'
  | 'ERNIE_API_KEY'
  | 'PADDLEOCR_API_URL'
  | 'PADDLE_OCR_TOKEN'
  | 'BAIDU_APP_KEY'
  | 'BAIDU_SECRET_KEY'

type SecretFieldKey =
  | 'PADDLEOCR_API_URL'
  | 'DEEPSEEK_API_KEY'
  | 'ERNIE_API_KEY'
  | 'PADDLE_OCR_TOKEN'
  | 'BAIDU_APP_KEY'
  | 'BAIDU_SECRET_KEY'

interface FieldMeta {
  key: RuntimeFormKey
  label: string
  placeholder: string
  description: string
}

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const saving = ref(false)
const probing = ref(false)
const error = ref('')
const success = ref('')
const probeMessage = ref('')
const probeStatus = ref<'idle' | 'success' | 'error'>('idle')
const envFilePath = ref('')
const speechAvailable = ref(false)
const models = ref<Array<{ key: string; label: string; available: boolean }>>([])
const activeBackendBase = ref(getRuntimeApiBaseUrl())
const backendConfigLoaded = ref(false)

const form = reactive<Record<RuntimeFormKey, string>>({
  apiBaseUrl: getRuntimeApiBaseUrl(),
  LOCAL_USER_NAME: '',
  DEEPSEEK_BASE_URL: '',
  DEEPSEEK_API_KEY: '',
  ERNIE_BASE_URL: '',
  ERNIE_API_KEY: '',
  PADDLEOCR_API_URL: '',
  PADDLE_OCR_TOKEN: '',
  BAIDU_APP_KEY: '',
  BAIDU_SECRET_KEY: '',
})

const configured = reactive<Record<string, boolean>>({})
const displayValues = reactive<Record<string, string>>({})
const clearSecretFlags = reactive<Record<SecretFieldKey, boolean>>({
  PADDLEOCR_API_URL: false,
  DEEPSEEK_API_KEY: false,
  ERNIE_API_KEY: false,
  PADDLE_OCR_TOKEN: false,
  BAIDU_APP_KEY: false,
  BAIDU_SECRET_KEY: false,
})

const profileFields: FieldMeta[] = [
  {
    key: 'LOCAL_USER_NAME',
    label: '本机用户名',
    placeholder: '例如：张三 / 前端调试机',
    description: '单机模式下显示在界面右上角、历史记录和本地工作区中的名称。',
  },
]

const networkFields: FieldMeta[] = [
  {
    key: 'apiBaseUrl',
    label: '前端 API_URL',
    placeholder: '留空则使用同源地址 / 桌面版内置地址',
    description: '控制前端请求发往哪个后端服务，保存后后续请求立即生效。',
  },
  {
    key: 'DEEPSEEK_BASE_URL',
    label: 'DeepSeek API_URL',
    placeholder: 'https://api.deepseek.com/v1',
    description: '兼容 OpenAI 协议的模型网关地址。',
  },
  {
    key: 'ERNIE_BASE_URL',
    label: '文心 API_URL',
    placeholder: 'https://aistudio.baidu.com/llm/lmapi/v3',
    description: '百度文心模型调用地址。',
  },
]

const secretFields: Array<FieldMeta & { key: SecretFieldKey }> = [
  {
    key: 'PADDLEOCR_API_URL',
    label: 'PaddleOCR API_URL',
    placeholder: '留空表示保持现有值',
    description: 'OCR 服务地址，作为私密配置由用户在本机自行注入。',
  },
  {
    key: 'DEEPSEEK_API_KEY',
    label: 'DeepSeek API_KEY',
    placeholder: '留空表示保持现有值',
    description: '用于 DeepSeek 模型调用。',
  },
  {
    key: 'ERNIE_API_KEY',
    label: '文心 API_KEY',
    placeholder: '留空表示保持现有值',
    description: '用于百度文心模型调用。',
  },
  {
    key: 'PADDLE_OCR_TOKEN',
    label: 'PaddleOCR Token',
    placeholder: '留空表示保持现有值',
    description: '用于 OCR 服务鉴权。',
  },
  {
    key: 'BAIDU_APP_KEY',
    label: '百度语音 App Key',
    placeholder: '留空表示保持现有值',
    description: '用于语音识别 / 语音合成。',
  },
  {
    key: 'BAIDU_SECRET_KEY',
    label: '百度语音 Secret Key',
    placeholder: '留空表示保持现有值',
    description: '与 App Key 配套使用。',
  },
]

const currentApiBaseLabel = computed(() => describeRuntimeApiBaseUrl(form.apiBaseUrl))
const activeBackendLabel = computed(() => describeRuntimeApiBaseUrl(activeBackendBase.value))

function goBack() {
  router.push('/')
}

function applySnapshot(snapshot: RuntimeConfigResponse) {
  envFilePath.value = snapshot.env_file_path || ''
  speechAvailable.value = !!snapshot.speech_available
  models.value = Array.isArray(snapshot.models) ? snapshot.models : []
  form.LOCAL_USER_NAME = snapshot.fields?.LOCAL_USER_NAME?.value || '本地用户'
  configured.LOCAL_USER_NAME = !!snapshot.fields?.LOCAL_USER_NAME?.configured
  displayValues.LOCAL_USER_NAME = snapshot.fields?.LOCAL_USER_NAME?.display_value || form.LOCAL_USER_NAME

  for (const field of networkFields) {
    if (field.key === 'apiBaseUrl') {
      continue
    }
    const nextValue = snapshot.fields?.[field.key]?.value || ''
    form[field.key] = nextValue
    configured[field.key] = !!snapshot.fields?.[field.key]?.configured
    displayValues[field.key] = snapshot.fields?.[field.key]?.display_value || nextValue
  }

  for (const field of secretFields) {
    form[field.key] = ''
    configured[field.key] = !!snapshot.fields?.[field.key]?.configured
    displayValues[field.key] = snapshot.fields?.[field.key]?.display_value || ''
    clearSecretFlags[field.key] = false
  }
}

async function loadConfig() {
  loading.value = true
  error.value = ''
  try {
    activeBackendBase.value = getRuntimeApiBaseUrl()
    form.apiBaseUrl = getRuntimeApiBaseUrl()
    const snapshot = await fetchRuntimeConfig(activeBackendBase.value)
    applySnapshot(snapshot)
    backendConfigLoaded.value = true
  } catch (err) {
    backendConfigLoaded.value = false
    error.value = err instanceof Error ? err.message : '读取配置失败'
  } finally {
    loading.value = false
  }
}

async function handleProbeApi() {
  probing.value = true
  probeMessage.value = ''
  probeStatus.value = 'idle'

  try {
    await probeApiHealth(form.apiBaseUrl)
    probeStatus.value = 'success'
    probeMessage.value = `连接成功：${currentApiBaseLabel.value}`
  } catch (err) {
    probeStatus.value = 'error'
    probeMessage.value = err instanceof Error ? err.message : '连接失败'
  } finally {
    probing.value = false
  }
}

async function handleSave() {
  saving.value = true
  error.value = ''
  success.value = ''
  let apiUrlPersisted = false

  try {
    const previousBase = getRuntimeApiBaseUrl()
    const nextApiBase = setRuntimeApiBaseUrl(form.apiBaseUrl)
    apiUrlPersisted = previousBase !== nextApiBase
    activeBackendBase.value = nextApiBase
    form.apiBaseUrl = nextApiBase

    if (!backendConfigLoaded.value) {
      success.value = 'API_URL 已保存。当前后端未连通，本机用户名、密钥与网关地址尚未写入后端 .env。'
      return
    }

    const payload: Record<string, string> = {
      LOCAL_USER_NAME: form.LOCAL_USER_NAME.trim(),
      DEEPSEEK_BASE_URL: form.DEEPSEEK_BASE_URL.trim(),
      ERNIE_BASE_URL: form.ERNIE_BASE_URL.trim(),
    }

    for (const field of secretFields) {
      const nextValue = form[field.key].trim()
      if (clearSecretFlags[field.key]) {
        payload[field.key] = ''
      } else if (nextValue) {
        payload[field.key] = nextValue
      }
    }

    const snapshot = await saveRuntimeConfig(payload, previousBase)
    applySnapshot(snapshot)
    await auth.tryRestore()
    success.value = snapshot.message || '应用设置已保存'
  } catch (err) {
    const message = err instanceof Error ? err.message : '保存失败'
    error.value = apiUrlPersisted
      ? `${message}；前端 API_URL 已更新`
      : message
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 rounded-full border border-slate-200/80 bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500 shadow-sm dark:border-slate-800 dark:bg-slate-900/70 dark:text-slate-400">
          <Settings class="h-3.5 w-3.5" />
          App Settings
        </div>
        <h1 class="mt-3 text-3xl font-semibold tracking-tight text-slate-900 dark:text-white">应用设置</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">
          这是单机版的统一设置入口。你可以在这里修改本机用户名、前后端连接地址和各模型密钥，保存后新的请求会直接使用最新配置。
        </p>
      </div>
      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:border-slate-600 dark:hover:bg-slate-800"
        @click="goBack"
      >
        <ArrowLeft class="h-4 w-4" />
        返回
      </button>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <section class="rounded-3xl border border-slate-200/80 bg-white/85 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
        <div class="mb-6 flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-slate-900 dark:text-white">连接与密钥</h2>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">留空的私密字段不会覆盖现有值。勾选清空后会把对应值写为空。</p>
          </div>
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-900"
            :disabled="loading"
            @click="loadConfig"
          >
            <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
            刷新
          </button>
        </div>

        <div v-if="error" class="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-300">
          {{ error }}
        </div>
        <div v-if="success" class="mb-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700 dark:border-emerald-900/60 dark:bg-emerald-950/40 dark:text-emerald-300">
          {{ success }}
        </div>

        <div class="space-y-5">
          <div class="rounded-2xl border border-slate-200/80 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-900/60">
            <h3 class="text-sm font-medium text-slate-800 dark:text-slate-100">本机身份</h3>
            <p class="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">不再使用登录页；应用默认以当前设备上的单个本地用户运行。</p>
            <div class="mt-4 space-y-4">
              <div v-for="field in profileFields" :key="field.key">
                <label :for="field.key" class="block text-sm font-medium text-slate-800 dark:text-slate-100">{{ field.label }}</label>
                <p class="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">{{ field.description }}</p>
                <input
                  :id="field.key"
                  v-model="form[field.key]"
                  type="text"
                  class="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-200 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:border-indigo-500 dark:focus:ring-indigo-950"
                  :placeholder="field.placeholder"
                />
              </div>
            </div>
          </div>

          <div v-for="field in networkFields" :key="field.key" class="rounded-2xl border border-slate-200/80 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-900/60">
            <label :for="field.key" class="block text-sm font-medium text-slate-800 dark:text-slate-100">{{ field.label }}</label>
            <p class="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">{{ field.description }}</p>
            <input
              :id="field.key"
              v-model="form[field.key]"
              type="text"
              class="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-200 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:border-indigo-500 dark:focus:ring-indigo-950"
              :placeholder="field.placeholder"
            />
            <div v-if="field.key === 'apiBaseUrl'" class="mt-3 flex flex-wrap items-center gap-3">
              <span class="rounded-full bg-slate-200 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                当前保存值：{{ currentApiBaseLabel }}
              </span>
              <button
                type="button"
                class="rounded-xl border border-slate-200 px-3 py-2 text-xs font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                :disabled="probing"
                @click="handleProbeApi"
              >
                {{ probing ? '检测中...' : '检测 API 连通性' }}
              </button>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200/80 bg-slate-50/70 p-4 dark:border-slate-800 dark:bg-slate-900/60">
            <h3 class="text-sm font-medium text-slate-800 dark:text-slate-100">敏感配置</h3>
            <p class="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">已配置的私密地址和密钥会以掩码显示。输入新值才会覆盖。</p>
            <div class="mt-4 space-y-4">
              <div v-for="field in secretFields" :key="field.key" class="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-950/80">
                <label :for="field.key" class="block text-sm font-medium text-slate-800 dark:text-slate-100">{{ field.label }}</label>
                <p class="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">{{ field.description }}</p>
                <div v-if="configured[field.key]" class="mt-2 rounded-xl bg-slate-100 px-3 py-2 text-xs text-slate-600 dark:bg-slate-900 dark:text-slate-300">
                  当前值：{{ displayValues[field.key] || '已配置' }}
                </div>
                <input
                  :id="field.key"
                  v-model="form[field.key]"
                  type="password"
                  class="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-200 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:border-indigo-500 dark:focus:ring-indigo-950"
                  :placeholder="field.placeholder"
                />
                <label class="mt-3 inline-flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <input v-model="clearSecretFlags[field.key]" type="checkbox" class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-900" />
                  清空这个密钥
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex flex-wrap items-center gap-3">
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="loading || saving"
            @click="handleSave"
          >
            {{ saving ? '保存中...' : '保存配置' }}
          </button>
          <span v-if="probeMessage" class="text-sm" :class="probeStatus === 'success' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
            {{ probeMessage }}
          </span>
        </div>
      </section>

      <aside class="space-y-6">
        <section class="rounded-3xl border border-slate-200/80 bg-white/85 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">当前运行状态</h2>
          <div class="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-slate-400">Local User</div>
              <div class="mt-1">{{ form.LOCAL_USER_NAME || '本地用户' }}</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-slate-400">Active Backend</div>
              <div class="mt-1 break-all">{{ activeBackendLabel }}</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-slate-400">Env File</div>
              <div class="mt-1 break-all">{{ envFilePath || '未读取到' }}</div>
            </div>
            <div>
              <div class="text-xs uppercase tracking-[0.2em] text-slate-400">Speech</div>
              <div class="mt-1">{{ speechAvailable ? '已配置' : '未配置' }}</div>
            </div>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-200/80 bg-white/85 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">模型可用性</h2>
          <div class="mt-4 space-y-3">
            <div
              v-for="model in models"
              :key="model.key"
              class="flex items-center justify-between rounded-2xl border border-slate-200/80 bg-slate-50/80 px-4 py-3 dark:border-slate-800 dark:bg-slate-900/70"
            >
              <div>
                <div class="font-medium text-slate-800 dark:text-slate-100">{{ model.label }}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400">{{ model.key }}</div>
              </div>
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="model.available ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300' : 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'">
                {{ model.available ? '可用' : '未配置' }}
              </span>
            </div>
            <div v-if="!models.length" class="rounded-2xl border border-dashed border-slate-300 px-4 py-5 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
              尚未读取到模型状态。
            </div>
          </div>
        </section>

        <section class="rounded-3xl border border-slate-200/80 bg-white/85 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">说明</h2>
          <ul class="mt-4 space-y-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
            <li>单机版默认使用当前设备上的一个本地用户，不再需要登录或注册。</li>
            <li>前端 `API_URL` 存在浏览器本地存储里，修改后新的请求会立刻走新地址。</li>
            <li>模型与 OCR 密钥会写入后端运行时 `.env`，后端会同步刷新可用模型列表。</li>
            <li>如果你想恢复默认开发模式，把前端 `API_URL` 清空即可。</li>
          </ul>
        </section>
      </aside>
    </div>
  </div>
</template>
