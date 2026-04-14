<script setup lang="ts">
import { ref, computed, onBeforeUnmount, onMounted, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from './stores/theme'
import { useInterviewStore } from './stores/interview'
import { useAuthStore } from './stores/auth'
import BlobBackground from './components/BlobBackground.vue'
import {
  Bot, Settings,
  Sun, Moon, ArrowLeft, MessageSquare, BookOpen, Sparkles, FilePlus2, History, FileUser, ChevronLeft, ChevronRight,
  SlidersHorizontal, ClipboardList, Map
} from 'lucide-vue-next'

const CatLoading = defineAsyncComponent(() => import('./components/CatLoading.vue'))

const theme = useThemeStore()
const interview = useInterviewStore()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const isRouteLoading = ref(false)
const pendingRouteName = ref('')
const SIDEBAR_COLLAPSED_KEY = 'proview:sidebar-collapsed'
const isSidebarCollapsed = ref(localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1')
let routeLoadingTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  interview.rehydrateInterviewSession()
})

const isGuestPage = computed(() => route.meta.guest === true)

const routeLoadingMessageMap: Record<string, string> = {
  'runtime-config': '正在加载接口配置页...',
  setup: '正在加载面试配置页...',
  interview: '正在进入面试房间...',
  report: '正在加载评估报告...',
  'report-history': '正在加载历史报告...',
  summary: '正在整理面经总结...',
  history: '正在加载面试历史...',
  'history-detail': '正在打开历史详情...',
  'resume-optimizer': '正在加载简历优化页...',
  'resume-builder': '正在加载简历生成页...',
  'my-resumes': '正在加载我的简历...',
  'career-planning': '正在加载职业规划工作台...',
  'career-planning-overview': '正在加载职业规划总览页...',
  'career-planning-roadmap': '正在加载职业规划路线图页...',
  'career-planning-tasks': '正在加载职业规划任务页...',
  'career-planning-docs': '正在加载职业规划文档页...',
}

const routeLoadingMessage = computed(() => {
  const routeName = pendingRouteName.value || (typeof route.name === 'string' ? route.name : '')
  return routeLoadingMessageMap[routeName] || '页面加载中，请稍候...'
})

const routeLoadingStage = computed(() => (
  route.meta.guest ? '正在准备页面资源' : '你仍然可以继续滚动和查看当前界面'
))

function clearRouteLoadingTimer() {
  if (routeLoadingTimer) {
    clearTimeout(routeLoadingTimer)
    routeLoadingTimer = null
  }
}

function startRouteLoading(routeName = '') {
  pendingRouteName.value = routeName
  clearRouteLoadingTimer()
  routeLoadingTimer = setTimeout(() => {
    isRouteLoading.value = true
  }, 120)
}

function finishRouteLoading() {
  clearRouteLoadingTimer()
  isRouteLoading.value = false
  pendingRouteName.value = ''
}

const removeRouteErrorHandler = router.onError(() => {
  finishRouteLoading()
})

const removeRouteLoadingStart = router.beforeEach((to, from) => {
  if (!from.matched.length || to.fullPath === from.fullPath) return
  startRouteLoading(typeof to.name === 'string' ? to.name : '')
})

const removeRouteLoadingEnd = router.afterEach(() => {
  finishRouteLoading()
})

const navItems = computed(() => [
  { name: 'setup', icon: SlidersHorizontal, label: '面试配置', path: '/', group: '面试流程' },
  { name: 'history', icon: History, label: '面试历史', path: '/history', group: '面试流程' },
  { name: 'interview', icon: MessageSquare, label: '面试房间', path: '/interview', disabled: !interview.canEnterInterviewRoom, group: '面试流程' },
  { name: 'report', icon: ClipboardList, label: '评估报告', path: '/report', group: '面试流程' },
  { name: 'summary', icon: BookOpen, label: '面经总结', path: '/summary', group: '面试流程' },
  { name: 'runtime-config', icon: Settings, label: '接口配置', path: '/config', group: '工具箱' },
  { name: 'resume-optimizer', icon: Sparkles, label: '简历优化', path: '/resume-optimizer', group: '工具箱' },
  { name: 'resume-builder', icon: FilePlus2, label: '简历生成', path: '/resume-builder', group: '工具箱' },
  { name: 'my-resumes', icon: FileUser, label: '我的简历', path: '/my-resumes', group: '工具箱' },
  { name: 'career-planning', icon: Map, label: '职业规划', routeName: 'career-planning-overview', path: '/career-planning/overview', group: '工具箱' },
])

const currentNav = computed(() => {
  if (route.name === 'interview') return 'interview'
  if (route.name === 'report' || route.name === 'report-history') return 'report'
  if (route.name === 'summary') return 'summary'
  if (route.name === 'runtime-config') return 'runtime-config'
  if (route.name === 'history' || route.name === 'history-detail') return 'history'
  if (route.name === 'resume-optimizer') return 'resume-optimizer'
  if (route.name === 'resume-builder') return 'resume-builder'
  if (route.name === 'my-resumes') return 'my-resumes'
  if (typeof route.name === 'string' && route.name.startsWith('career-planning')) return 'career-planning'
  return 'setup'
})

function navigateTo(item: { name?: string; path: string; routeName?: string; disabled?: boolean }) {
  if (item.disabled) return
  const targetName = item.routeName || item.name || ''
  const targetPath = item.path
  if ((targetName && route.name === targetName) || (!targetName && route.path === targetPath)) {
    return
  }

  startRouteLoading(targetName)

  if (item.routeName) {
    router.push({ name: item.routeName }).catch(() => finishRouteLoading())
    return
  }
  router.push(item.path).catch(() => finishRouteLoading())
}

function getNavItemClass(item: { name: string; disabled?: boolean }, activeClass: string, idleClass: string, disabledClass: string) {
  if (currentNav.value === item.name) return activeClass
  if (item.disabled) return disabledClass
  return idleClass
}

function handleThemeToggle(e: MouseEvent) {
  theme.toggle(e.currentTarget as HTMLElement)
}

function goLanding() {
  window.location.href = '/'
}

function openSettings() {
  if (route.name === 'runtime-config') return
  router.push('/config')
}

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, isSidebarCollapsed.value ? '1' : '0')
}

onBeforeUnmount(() => {
  clearRouteLoadingTimer()
  removeRouteErrorHandler()
  removeRouteLoadingStart()
  removeRouteLoadingEnd()
})
</script>

<template>
  <div class="flex h-screen w-full overflow-hidden bg-slate-50 font-sans text-slate-900 transition-colors duration-500 dark:bg-[#05050A] dark:text-slate-300">

    <!-- ================== PC端：左侧边栏 ================== -->
    <aside
      v-if="!isGuestPage"
      class="z-20 hidden min-h-0 flex-col overflow-hidden border-r border-slate-200/80 bg-white/90 transition-[width] duration-300 md:flex dark:border-white/5 dark:bg-[#0A0A0F]/95"
      :class="isSidebarCollapsed ? 'w-24' : 'w-64'"
    >
      <!-- Logo -->
      <div class="flex h-20 shrink-0 items-center border-b border-slate-100 dark:border-white/5" :class="isSidebarCollapsed ? 'px-3' : 'px-6'">
        <div class="flex min-w-0 flex-1 items-center" :class="isSidebarCollapsed ? 'justify-center' : 'gap-3'">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30 dark:shadow-indigo-900/40">
            <Bot class="w-5 h-5" />
          </div>
          <span
            v-if="!isSidebarCollapsed"
            class="truncate text-xl font-extrabold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-700 dark:from-white dark:to-indigo-200"
          >
            ProView AI
          </span>
        </div>
        <button
          type="button"
          class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-slate-200/80 bg-slate-50/80 text-slate-600 transition hover:border-slate-300 hover:bg-white hover:text-primary dark:border-white/10 dark:bg-white/5 dark:text-slate-300 dark:hover:bg-white/10 dark:hover:text-indigo-300"
          :title="isSidebarCollapsed ? '展开导航栏' : '折叠导航栏'"
          @click="toggleSidebar"
        >
          <ChevronRight v-if="isSidebarCollapsed" class="h-4 w-4" />
          <ChevronLeft v-else class="h-4 w-4" />
        </button>
      </div>

      <div class="custom-scroll min-h-0 flex-1 overflow-y-auto overscroll-contain">
        <div class="px-4 pt-4">
          <button
            type="button"
            @click="handleThemeToggle"
            class="flex w-full items-center rounded-2xl border border-slate-200/80 bg-slate-50/80 py-3 text-sm font-semibold text-slate-700 shadow-sm transition-all hover:border-slate-300 hover:bg-white hover:text-primary dark:border-white/10 dark:bg-white/5 dark:text-slate-200 dark:hover:bg-white/10 dark:hover:text-indigo-300"
            :class="isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4'"
            :title="theme.isDark ? '切换到浅色模式' : '切换到深色模式'"
          >
            <Sun v-if="theme.isDark" class="w-5 h-5 text-amber-400" />
            <Moon v-else class="w-5 h-5" />
            <span v-if="!isSidebarCollapsed">{{ theme.isDark ? '浅色模式' : '深色模式' }}</span>
          </button>
        </div>

        <!-- 导航菜单 -->
        <nav class="mt-4 flex flex-col gap-2 px-4 pb-4">
          <div v-if="!isSidebarCollapsed" class="mb-2 px-2 text-xs font-bold uppercase tracking-wider text-slate-400">面试流程</div>
          <button
            v-for="item in navItems.filter(i => i.group === '面试流程')" :key="item.name"
            @click="navigateTo(item)"
            class="group flex items-center rounded-xl py-3 text-sm font-bold transition-all"
            :class="[
              isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4',
              getNavItemClass(
                item,
                'bg-indigo-600 text-white shadow-md dark:bg-primary dark:shadow-[0_0_15px_rgba(79,70,229,0.3)]',
                'text-slate-600 hover:bg-slate-100 hover:text-indigo-600 dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-indigo-300',
                'text-slate-300 dark:text-slate-600 cursor-not-allowed'
              )
            ]"
            :disabled="item.disabled"
            :title="isSidebarCollapsed ? item.label : undefined"
          >
            <component :is="item.icon" class="w-5 h-5 transition-transform group-hover:scale-110" />
            <span v-if="!isSidebarCollapsed">{{ item.label }}</span>
          </button>
          <div v-if="!isSidebarCollapsed" class="mt-4 mb-2 px-2 text-xs font-bold uppercase tracking-wider text-slate-400">工具箱</div>
          <button
            v-for="item in navItems.filter(i => i.group === '工具箱')" :key="item.name"
            @click="navigateTo(item)"
            class="group flex items-center rounded-xl py-3 text-sm font-bold transition-all"
            :class="[
              isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4',
              currentNav === item.name
                ? 'bg-indigo-600 text-white shadow-md dark:bg-primary dark:shadow-[0_0_15px_rgba(79,70,229,0.3)]'
                : 'text-slate-600 hover:bg-slate-100 hover:text-indigo-600 dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-indigo-300'
            ]"
            :title="isSidebarCollapsed ? item.label : undefined"
          >
            <component :is="item.icon" class="w-5 h-5 transition-transform group-hover:scale-110" />
            <span v-if="!isSidebarCollapsed">{{ item.label }}</span>
          </button>
        </nav>
      </div>

      <!-- 底部控制 -->
      <div class="shrink-0 space-y-2 border-t border-slate-100 p-4 dark:border-white/5">
        <button
          @click="goLanding"
          class="flex w-full items-center rounded-xl py-3 text-sm font-semibold text-slate-600 transition-all hover:bg-slate-100 hover:text-primary dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-indigo-300"
          :class="isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4'"
          :title="isSidebarCollapsed ? '返回介绍页' : undefined"
        >
          <ArrowLeft class="w-5 h-5" />
          <span v-if="!isSidebarCollapsed">返回介绍页</span>
        </button>
        <button
          @click="openSettings"
          class="flex w-full items-center rounded-xl py-3 text-sm font-semibold text-slate-600 transition-all hover:bg-slate-100 hover:text-primary dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-indigo-300"
          :class="isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4'"
          :title="isSidebarCollapsed ? '应用设置' : undefined"
        >
          <Settings class="w-5 h-5" />
          <span v-if="!isSidebarCollapsed">应用设置</span>
        </button>
        <div class="rounded-2xl border border-slate-200/80 bg-slate-50/80 py-3 dark:border-white/5 dark:bg-white/5" :class="isSidebarCollapsed ? 'px-3' : 'px-4'">
          <div class="flex items-center" :class="isSidebarCollapsed ? 'justify-center' : 'gap-3'">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-500/20">
              <Bot class="h-4 w-4" />
            </div>
            <div v-if="!isSidebarCollapsed" class="min-w-0">
              <p class="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">单机模式</p>
              <p class="mt-1 truncate text-sm font-semibold text-slate-700 dark:text-slate-200">{{ auth.user?.display_name || auth.user?.username || '本地用户' }}</p>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- ================== 移动端：底部 Tab ================== -->
    <nav v-if="!isGuestPage" class="fixed bottom-0 left-0 right-0 z-50 border-t border-slate-200 bg-white/95 pb-2 pt-2 md:hidden dark:border-white/10 dark:bg-[#0A0A0F]/95">
      <div class="flex justify-around">
        <button
          v-for="item in navItems" :key="item.name"
          @click="navigateTo(item)"
          class="flex flex-col items-center p-2 transition-colors"
          :class="getNavItemClass(
            item,
            'text-primary dark:text-indigo-400',
            'text-slate-500 dark:text-slate-400',
            'text-slate-300 dark:text-slate-600'
          )"
          :disabled="item.disabled"
        >
          <component :is="item.icon" class="mb-1 w-5 h-5" />
          <span class="text-[10px] font-bold">{{ item.label }}</span>
        </button>
        <button @click="goLanding" class="flex flex-col items-center p-2 text-slate-500 transition-colors dark:text-slate-400">
          <ArrowLeft class="mb-1 w-5 h-5" />
          <span class="text-[10px] font-bold">介绍页</span>
        </button>
      </div>
    </nav>

    <!-- ================== 右侧主内容区 ================== -->
    <main class="custom-scroll relative z-10 min-h-0 flex-1 overflow-y-auto overscroll-contain pb-20 md:pb-0">
      <BlobBackground />
      <div class="relative z-10 min-h-full">
        <div v-if="!isGuestPage" class="pointer-events-none absolute left-4 top-4 z-20 md:hidden">
          <button
            type="button"
            class="pointer-events-auto inline-flex h-11 w-11 items-center justify-center rounded-full border border-slate-200/80 bg-white/90 text-slate-700 shadow-sm backdrop-blur transition hover:border-slate-300 hover:bg-white dark:border-white/10 dark:bg-slate-950/85 dark:text-slate-200 dark:hover:bg-slate-900"
            :title="theme.isDark ? '切换到浅色模式' : '切换到深色模式'"
            @click="handleThemeToggle"
          >
            <Sun v-if="theme.isDark" class="h-5 w-5 text-amber-400" />
            <Moon v-else class="h-5 w-5" />
          </button>
        </div>
        <div v-if="!isGuestPage" class="pointer-events-none absolute right-4 top-4 z-20 flex items-center gap-3">
          <div class="pointer-events-auto hidden items-center gap-3 rounded-full border border-slate-200/80 bg-white/90 px-4 py-2 text-sm text-slate-700 shadow-sm backdrop-blur md:flex dark:border-white/10 dark:bg-slate-950/85 dark:text-slate-200">
            <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">单机模式</span>
            <span class="max-w-[180px] truncate font-semibold">{{ auth.user?.display_name || auth.user?.username || '本地用户' }}</span>
          </div>
          <button
            type="button"
            class="pointer-events-auto inline-flex items-center gap-2 rounded-full border border-slate-200/80 bg-white/90 px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-white dark:border-white/10 dark:bg-slate-950/85 dark:text-slate-200 dark:hover:bg-slate-900"
            @click="openSettings"
          >
            <Settings class="h-4 w-4" />
            <span class="hidden sm:inline">设置</span>
          </button>
        </div>
        <div
          class="container mx-auto max-w-7xl px-4 sm:px-8"
          :class="isGuestPage ? 'py-8' : 'pb-8 pt-24 md:py-8'"
        >
          <router-view v-slot="{ Component, route: viewRoute }">
            <keep-alive :include="['InterviewView']">
              <component :is="Component" :key="viewRoute.fullPath" />
            </keep-alive>
          </router-view>
        </div>
      </div>
    </main>

    <CatLoading
      v-if="isRouteLoading"
      variant="corner"
      :blocking="false"
      :message="routeLoadingMessage"
      :stage="routeLoadingStage"
    />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
