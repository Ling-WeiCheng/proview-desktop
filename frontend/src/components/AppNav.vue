<script setup lang="ts">
import { useThemeStore } from '../stores/theme'
import { useInterviewStore } from '../stores/interview'
import { useRouter } from 'vue-router'
import { Bot, Terminal, Sun, Moon } from 'lucide-vue-next'

const theme = useThemeStore()
const interview = useInterviewStore()
const router = useRouter()

defineEmits<{ 'toggle-debug': [] }>()

function resetApp() {
  interview.reset()
  router.push('/')
}
</script>

<template>
  <nav class="fixed top-0 w-full glass-panel z-50 transition-all duration-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-20">
        <div class="flex items-center gap-3">
          <div class="relative group">
            <div class="absolute inset-0 bg-blue-500 dark:bg-indigo-500 blur-lg opacity-30 dark:opacity-50 group-hover:opacity-100 transition duration-500"></div>
            <div class="relative bg-blue-600 dark:bg-gradient-to-br dark:from-indigo-500 dark:to-purple-600 p-2.5 rounded-xl">
              <Bot class="w-6 h-6 text-white" />
            </div>
          </div>
          <span class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700 dark:from-white dark:via-indigo-200 dark:to-purple-200 tracking-wide">
            ProView AI
          </span>
        </div>
        <div class="flex items-center gap-5">
          <button @click="$emit('toggle-debug')" class="p-2 rounded-full text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-white/10 transition-colors" title="调试控制台">
            <Terminal class="w-5 h-5" />
          </button>
          <button @click="theme.toggle()" class="p-2 rounded-full text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-white/10 transition-colors">
            <Sun v-if="theme.isDark" class="w-5 h-5" />
            <Moon v-else class="w-5 h-5" />
          </button>
          <button @click="resetApp" class="relative inline-flex h-10 active:scale-95 transition-transform">
            <span class="relative inline-flex items-center justify-center px-6 py-2 text-sm font-bold text-white bg-primary rounded-full hover:bg-indigo-700 transition-colors shadow-md">
              返回大厅
            </span>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>
