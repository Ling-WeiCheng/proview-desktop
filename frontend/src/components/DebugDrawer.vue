<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Cpu, X, RefreshCw, FileText } from 'lucide-vue-next'
import { useInterviewStore } from '../stores/interview'
import { useResumeStore } from '../stores/resume'
import { buildApiUrl } from '../services/runtimeConfig'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()
const store = useInterviewStore()
const resumeStore = useResumeStore()
const route = useRoute()

const isResumePage = computed(() => route.name === 'resume-optimizer')

const currentSysprompt = ref('')
const syspromptLoading = ref(false)
const syspromptError = ref('')

async function fetchSysprompt() {
  // 从 sessionStorage 获取 session_id
  const sessionId = sessionStorage.getItem('interview_session_id')
  if (!sessionId) {
    syspromptError.value = '无 session_id'
    return
  }
  
  syspromptLoading.value = true
  syspromptError.value = ''
  
  try {
    const response = await fetch(buildApiUrl(`/api/debug/sysprompt?session_id=${sessionId}`))
    const data = await response.json()
    
    if (data.status === 'success') {
      currentSysprompt.value = data.sysprompt
    } else {
      syspromptError.value = data.message || '获取失败'
    }
  } catch (e) {
    syspromptError.value = '请求失败'
  } finally {
    syspromptLoading.value = false
  }
}

// 监听 session_id 变化
watch(() => sessionStorage.getItem('interview_session_id'), (newId) => {
  if (newId) {
    fetchSysprompt()
  }
}, { immediate: true })
</script>

<script lang="ts">
export default {
  name: 'DebugDrawer',
}
</script>

<template>
  <div class="fixed right-0 top-0 h-full w-full md:w-[450px] bg-slate-900 shadow-[-10px_0_30px_rgba(0,0,0,0.5)] transform transition-transform duration-300 z-[100] flex flex-col border-l border-slate-700"
       :class="open ? 'translate-x-0' : 'translate-x-full'">
    <div class="p-4 border-b border-slate-800 flex justify-between items-center bg-black/50">
      <h3 class="text-emerald-400 font-mono font-bold flex items-center gap-2 text-sm">
        <Cpu class="w-4 h-4" /> Agent 大脑监控面板
      </h3>
      <div class="flex items-center gap-2">
        <button 
          @click="fetchSysprompt" 
          :disabled="syspromptLoading"
          class="text-slate-400 hover:text-emerald-400 transition-colors disabled:opacity-50"
          title="刷新 System Prompt"
        >
          <RefreshCw class="w-4 h-4" :class="{'animate-spin': syspromptLoading}" />
        </button>
        <button @click="emit('close')" class="text-slate-400 hover:text-white transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>
    </div>
    <div class="flex-1 p-4 overflow-y-auto custom-scroll text-xs font-mono text-slate-300 space-y-4">
      <!-- ========== 简历优化调试面板 ========== -->
      <template v-if="isResumePage">
        <div v-if="resumeStore.phase === 'upload'" class="text-slate-500 italic text-center mt-10">
          等待上传简历...<br/>上传后将显示简历提取 + LLM 分析过程
        </div>
        <template v-else>
          <!-- 状态概览 -->
          <div class="border border-slate-700 rounded-lg p-3 bg-slate-800/50">
            <div class="text-emerald-500 font-bold mb-2 border-b border-slate-700 pb-1">📋 简历优化状态</div>
            <div class="space-y-1">
              <div>阶段: <span class="text-cyan-400">{{ resumeStore.phase }}</span></div>
              <div>Sections: <span class="text-amber-400">{{ resumeStore.sections.length }}</span></div>
              <div>建议总数: <span class="text-amber-400">{{ resumeStore.suggestions.length }}</span></div>
              <div>待处理: <span class="text-amber-400">{{ resumeStore.pendingCount }}</span> | 已采纳: <span class="text-emerald-400">{{ resumeStore.acceptedCount }}</span> | 已忽略: <span class="text-slate-400">{{ resumeStore.rejectedCount }}</span></div>
              <div v-if="resumeStore.error" class="text-red-400 mt-1">❌ 错误: {{ resumeStore.error }}</div>
            </div>
          </div>
          <!-- 简历原文 -->
          <details v-if="resumeStore.ocrText" class="cursor-pointer border border-slate-700 rounded-lg p-3 bg-slate-800/50">
            <summary class="text-rose-400 font-bold hover:text-rose-300">🔍 简历原始解析内容</summary>
            <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-60 overflow-y-auto custom-scroll whitespace-pre-wrap leading-relaxed text-[11px]">
              {{ resumeStore.ocrText }}
            </div>
          </details>
          <!-- Sections 数据 -->
          <details class="cursor-pointer border border-slate-700 rounded-lg p-3 bg-slate-800/50">
            <summary class="text-indigo-400 font-bold hover:text-indigo-300">🧩 Sections 结构化数据</summary>
            <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-60 overflow-y-auto custom-scroll">
              <pre class="whitespace-pre-wrap text-[11px]">{{ JSON.stringify(resumeStore.sections, null, 2) }}</pre>
            </div>
          </details>
          <!-- Suggestions 数据 -->
          <details class="cursor-pointer border border-slate-700 rounded-lg p-3 bg-slate-800/50">
            <summary class="text-amber-400 font-bold hover:text-amber-300">💡 Suggestions 原始数据</summary>
            <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-60 overflow-y-auto custom-scroll">
              <pre class="whitespace-pre-wrap text-[11px]">{{ JSON.stringify(resumeStore.suggestions, null, 2) }}</pre>
            </div>
          </details>
        </template>
      </template>

      <!-- ========== 面试调试面板（原有） ========== -->
      <template v-else>
      <!-- 服务状态总览（始终显示） -->
      <div v-if="store.serviceStatus" class="border border-slate-700 rounded-lg p-3 bg-slate-800/50">
        <div class="text-emerald-500 font-bold mb-2 border-b border-slate-700 pb-1">🖥️ 后端服务状态</div>
        <div class="space-y-1.5">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" :class="store.serviceStatus.data_service.connected ? 'bg-emerald-400' : 'bg-red-400'"></span>
            <span :class="store.serviceStatus.data_service.connected ? 'text-emerald-400' : 'text-red-400'">
              数据服务: {{ store.serviceStatus.data_service.connected ? '已连接' : '未连接' }}
            </span>
          </div>
          <div v-if="store.serviceStatus.data_service.url" class="text-slate-500 text-[11px] pl-4 break-all">
            {{ store.serviceStatus.data_service.url }}
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" :class="store.serviceStatus.agent_available ? 'bg-emerald-400' : 'bg-amber-400'"></span>
            <span :class="store.serviceStatus.agent_available ? 'text-emerald-400' : 'text-amber-400'">
              Agent 引擎: {{ store.serviceStatus.agent_available ? '就绪' : '不可用' }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" :class="store.serviceStatus.ocr_available ? 'bg-emerald-400' : 'bg-amber-400'"></span>
            <span :class="store.serviceStatus.ocr_available ? 'text-emerald-400' : 'text-amber-400'">
              OCR 解析: {{ store.serviceStatus.ocr_available ? '就绪' : '不可用' }}
            </span>
          </div>
        </div>
      </div>
      <div v-else class="border border-slate-700 rounded-lg p-3 bg-slate-800/50">
        <div class="text-slate-500 text-center">后端未连接，请启动 Flask 服务</div>
      </div>

      <!-- ========== 当前 System Prompt 展示（实时显示上传给大模型的内容） ========== -->
      <div class="border border-indigo-500/50 rounded-lg p-3 bg-indigo-900/10">
        <div class="text-indigo-400 font-bold mb-2 border-b border-indigo-500/30 pb-1 flex items-center justify-between">
          <span class="flex items-center gap-2">
            <FileText class="w-4 h-4" /> 📋 当前 System Prompt
          </span>
          <span v-if="currentSysprompt" class="text-xs text-indigo-300/60">
            {{ currentSysprompt.length }} 字符 / ~{{ Math.ceil(currentSysprompt.length / 4) }} tokens
          </span>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="syspromptLoading" class="text-center py-4 text-indigo-400">
          <RefreshCw class="w-5 h-5 animate-spin mx-auto mb-2" />
          加载中...
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="syspromptError" class="text-center py-4 text-red-400">
          ❌ {{ syspromptError }}
        </div>
        
        <!-- Sysprompt 内容 -->
        <details v-else-if="currentSysprompt" class="cursor-pointer">
          <summary class="text-indigo-300 hover:text-indigo-200 text-xs mb-2">
            点击展开/收起完整内容
          </summary>
          <div class="p-2 bg-black/40 rounded text-slate-300 max-h-80 overflow-y-auto custom-scroll whitespace-pre-wrap leading-relaxed text-[11px] border border-indigo-500/20">
            {{ currentSysprompt }}
          </div>
        </details>
        
        <!-- 空状态 -->
        <div v-else class="text-slate-500 text-center py-4 italic">
          等待获取 System Prompt...<br/>
          <span class="text-xs">请先开始一次面试</span>
        </div>
      </div>

      <div v-if="store.debugLogs.length === 0" class="text-slate-500 italic text-center mt-4">
        等待 Agent 交互...<br/>面板将实时捕获系统提示词、记忆和工具调用过程
      </div>
      <div v-for="(log, idx) in store.debugLogs" :key="idx"
           class="border border-slate-700 rounded-lg p-3 bg-slate-800/50 hover:bg-slate-800 transition-colors">
        <div class="flex justify-between text-emerald-500 mb-2 border-b border-slate-700 pb-1">
          <span class="font-bold">[{{ log.time }}] {{ log.stage }}</span>
        </div>
        <!-- Agent 模式 -->
        <div class="mb-2 p-2 bg-slate-800/50 rounded border border-slate-700">
          <div :class="log.info.agent_mode === 'LangChain' ? 'text-emerald-400' : 'text-amber-400'" class="font-bold">
            {{ log.info.agent_mode === 'LangChain' ? '✅' : '⚠️' }} Agent模式: {{ log.info.agent_mode }}
          </div>
          <div class="text-slate-400 text-xs mt-1">
            可用工具: {{ log.info.tools_available?.length ? log.info.tools_available.join(', ') : '无(降级模式)' }}
          </div>
          <div v-if="log.info.prompt_source" class="text-xs mt-1"
            :class="log.info.prompt_source === 'prompt_generator' ? 'text-cyan-400' : 'text-slate-500'">
            Prompt来源: {{ log.info.prompt_source === 'prompt_generator' ? '🤖 PromptGenerator 动态生成' : '📄 静态模板' }}
          </div>
          <div v-if="log.info.model_provider" class="text-xs mt-1 text-violet-400">
            🤖 模型: {{ log.info.model_label || log.info.model_provider }} ({{ log.info.model_name }})
          </div>
          <div v-if="log.info.data_service" class="text-xs mt-1"
            :class="log.info.data_service.connected ? 'text-emerald-400' : 'text-red-400'">
            {{ log.info.data_service.connected ? '🟢' : '🔴' }} 数据服务:
            {{ log.info.data_service.connected ? '已连接' : '未连接' }}
            <span v-if="log.info.data_service.url" class="text-slate-500 ml-1">{{ log.info.data_service.url }}</span>
          </div>
        </div>
        <!-- OCR 调用状态 -->
        <div class="mb-2 p-2 rounded border"
             :class="{
               'bg-emerald-900/20 border-emerald-700': log.info.ocr_status === 'success',
               'bg-red-900/20 border-red-700': log.info.ocr_status === 'error',
               'bg-amber-900/20 border-amber-700': log.info.ocr_status === 'unavailable',
               'bg-slate-800/50 border-slate-700': !log.info.ocr_status || log.info.ocr_status === 'not_called'
             }">
          <div class="font-bold text-xs"
               :class="{
                 'text-emerald-400': log.info.ocr_status === 'success',
                 'text-red-400': log.info.ocr_status === 'error',
                 'text-amber-400': log.info.ocr_status === 'unavailable',
                 'text-slate-500': !log.info.ocr_status || log.info.ocr_status === 'not_called'
               }">
            {{ log.info.ocr_status === 'success' ? '✅ 简历解析成功' :
               log.info.ocr_status === 'error' ? '❌ 简历解析失败' :
               log.info.ocr_status === 'unavailable' ? '⚠️ OCR 模块不可用' :
               '⏭️ 未解析简历（未上传简历）' }}
          </div>
          <div v-if="log.info.ocr_status === 'success'" class="text-slate-400 text-xs mt-1">
            简历内容已完成提取，原文见下方「简历原始解析内容」
          </div>
          <div v-if="log.info.ocr_status === 'error'" class="text-red-300 text-xs mt-1">
            简历解析出错，请检查文件内容与后端日志
          </div>
        </div>
        <!-- 简历摘要 -->
        <details v-if="log.info.resume_summary" class="mb-2 cursor-pointer">
          <summary class="text-cyan-400 font-bold hover:text-cyan-300">📋 简历摘要（LLM 总结）</summary>
          <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-40 overflow-y-auto custom-scroll whitespace-pre-wrap leading-relaxed">
            {{ log.info.resume_summary }}
          </div>
        </details>
        <!-- OCR 原始解析 -->
        <details v-if="log.info.ocr_raw_text" class="mb-2 cursor-pointer">
          <summary class="text-rose-400 font-bold hover:text-rose-300">🔍 OCR 原始解析内容（输入给模型的简历原文）</summary>
          <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-60 overflow-y-auto custom-scroll whitespace-pre-wrap leading-relaxed text-[11px]">
            {{ log.info.ocr_raw_text }}
          </div>
        </details>
        <!-- RAG 知识库检索 -->
        <details v-if="log.info.rag_context" class="mb-2 cursor-pointer">
          <summary class="text-teal-400 font-bold hover:text-teal-300">📚 RAG 知识库检索结果</summary>
          <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-60 overflow-y-auto custom-scroll whitespace-pre-wrap leading-relaxed text-[11px]">
            {{ log.info.rag_context }}
          </div>
        </details>
        <details v-if="log.info.rag_details" class="mb-2 cursor-pointer">
          <summary class="text-emerald-300 font-bold hover:text-emerald-200">🔎 RAG 匹配详情</summary>
          <div class="mt-2 space-y-2">
            <div class="p-2 bg-black/40 rounded text-[11px] text-slate-300 leading-relaxed">
              <div>query: <span class="text-cyan-300">{{ log.info.rag_details.query || '-' }}</span></div>
              <div>job: <span class="text-cyan-300">{{ log.info.rag_details.job_title || '-' }}</span></div>
              <div>
                status:
                <span
                  class="ml-1"
                  :class="{
                    'text-emerald-400': log.info.rag_details.status === 'matched',
                    'text-amber-400': log.info.rag_details.status === 'empty' || log.info.rag_details.status === 'not_started',
                    'text-red-400': log.info.rag_details.status === 'error',
                  }"
                >
                  {{ log.info.rag_details.status || 'unknown' }}
                </span>
              </div>
              <div>
                filters:
                <span class="text-violet-300">difficulty={{ log.info.rag_details.difficulty || '-' }}</span>
                <span class="text-violet-300 ml-2">type={{ log.info.rag_details.interview_type || '-' }}</span>
                <span class="text-violet-300 ml-2">style={{ log.info.rag_details.style || '-' }}</span>
                <span class="text-violet-300 ml-2">stage={{ log.info.rag_details.stage || '-' }}</span>
              </div>
              <div>
                hits:
                <span class="text-emerald-400 ml-1">jobs={{ log.info.rag_details.counts?.jobs ?? 0 }}</span>
                <span class="text-emerald-400 ml-2">questions={{ log.info.rag_details.counts?.questions ?? 0 }}</span>
                <span class="text-emerald-400 ml-2">scripts={{ log.info.rag_details.counts?.scripts ?? 0 }}</span>
              </div>
              <div v-if="log.info.rag_details.error" class="mt-1 text-red-400 whitespace-pre-wrap">
                error: {{ log.info.rag_details.error }}
              </div>
            </div>

            <div v-if="log.info.rag_details.jobs?.length" class="p-2 bg-black/40 rounded">
              <div class="text-cyan-400 font-bold mb-1">岗位画像命中</div>
              <div v-for="(item, i) in log.info.rag_details.jobs" :key="`job-${i}`" class="mb-2 last:mb-0 text-[11px] text-slate-300 border border-slate-700 rounded p-2">
                <div class="text-emerald-300">#{{ i + 1 }} {{ item.id || '-' }}</div>
                <div class="mt-1 whitespace-pre-wrap">{{ item.document }}</div>
                <details class="mt-1">
                  <summary class="text-slate-400 hover:text-slate-300">metadata</summary>
                  <pre class="mt-1 whitespace-pre-wrap text-slate-400">{{ JSON.stringify(item.metadata, null, 2) }}</pre>
                </details>
              </div>
            </div>

            <div v-if="log.info.rag_details.questions?.length" class="p-2 bg-black/40 rounded">
              <div class="text-cyan-400 font-bold mb-1">题库命中</div>
              <div v-for="(item, i) in log.info.rag_details.questions" :key="`question-${i}`" class="mb-2 last:mb-0 text-[11px] text-slate-300 border border-slate-700 rounded p-2">
                <div class="text-emerald-300">#{{ i + 1 }} {{ item.id || '-' }}</div>
                <div class="mt-1 whitespace-pre-wrap">{{ item.document }}</div>
                <details class="mt-1">
                  <summary class="text-slate-400 hover:text-slate-300">metadata</summary>
                  <pre class="mt-1 whitespace-pre-wrap text-slate-400">{{ JSON.stringify(item.metadata, null, 2) }}</pre>
                </details>
              </div>
            </div>

            <div v-if="log.info.rag_details.scripts?.length" class="p-2 bg-black/40 rounded">
              <div class="text-cyan-400 font-bold mb-1">话术命中</div>
              <div v-for="(item, i) in log.info.rag_details.scripts" :key="`script-${i}`" class="mb-2 last:mb-0 text-[11px] text-slate-300 border border-slate-700 rounded p-2">
                <div class="text-emerald-300">#{{ i + 1 }} {{ item.id || '-' }}</div>
                <div class="mt-1 whitespace-pre-wrap">{{ item.document }}</div>
                <details class="mt-1">
                  <summary class="text-slate-400 hover:text-slate-300">metadata</summary>
                  <pre class="mt-1 whitespace-pre-wrap text-slate-400">{{ JSON.stringify(item.metadata, null, 2) }}</pre>
                </details>
              </div>
            </div>
          </div>
        </details>
        <!-- System Prompt -->
        <details class="mb-2 cursor-pointer">
          <summary class="text-indigo-400 font-bold hover:text-indigo-300">🧠 System Prompt</summary>
          <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-40 overflow-y-auto custom-scroll whitespace-pre-wrap leading-relaxed">
            {{ log.info.system_prompt || '无' }}
          </div>
        </details>
        <!-- Chat Memory -->
        <details class="mb-2 cursor-pointer">
          <summary class="text-blue-400 font-bold hover:text-blue-300">📖 Chat Memory</summary>
          <div class="mt-2 p-2 bg-black/40 rounded text-slate-400 max-h-40 overflow-y-auto custom-scroll">
            <pre class="whitespace-pre-wrap">{{ JSON.stringify(log.info.chat_history, null, 2) }}</pre>
          </div>
        </details>
        <!-- 工具调用 -->
        <div v-if="log.info.intermediate_steps?.length" class="mt-2 pl-2 border-l-2 border-amber-500/50 text-amber-300/80 space-y-2">
          <div class="font-bold text-amber-500">🔧 工具调用 ({{ log.info.intermediate_steps.length }}步)</div>
          <div v-for="(step, si) in log.info.intermediate_steps" :key="si"
               class="bg-black/30 p-2 rounded border border-amber-900/30">
            <div class="text-amber-400 font-bold mb-1">Action: {{ step.tool }}</div>
            <div class="text-slate-400 break-words">Input: {{ JSON.stringify(step.tool_input) }}</div>
            <div class="text-slate-500 mt-1 max-h-20 overflow-y-auto hover:max-h-none cursor-pointer">
              Observation: {{ step.observation }}
            </div>
          </div>
        </div>
        <div v-else class="mt-2 p-2 bg-slate-800/50 rounded border border-slate-700">
          <div class="text-slate-500 text-xs">本轮无工具调用</div>
        </div>
      </div>
      </template>
    </div>
  </div>
</template>
