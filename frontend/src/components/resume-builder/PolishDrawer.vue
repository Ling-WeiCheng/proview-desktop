<script setup lang="ts">
import { computed } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import { X, Check, XCircle, Sparkles } from 'lucide-vue-next'

const store = useResumeBuilderStore()

const pendingSuggestions = computed(() =>
  store.document.polishSuggestions.filter(suggestion => suggestion.status === 'pending')
)

function close() {
  store.polishDrawerOpen = false
}

function handleAccept(suggestionId: string) {
  store.acceptPolish(suggestionId)
}

function handleReject(suggestionId: string) {
  store.rejectPolish(suggestionId)
}
</script>

<template>
  <div>
    <Transition name="fade">
      <div
        v-if="store.polishDrawerOpen"
        class="fixed inset-0 z-40 bg-black/35"
        @click="close"
      />
    </Transition>

    <Transition name="slide-right">
      <aside
        v-if="store.polishDrawerOpen"
        class="fixed right-0 top-0 bottom-0 z-50 flex w-full flex-col bg-white shadow-2xl sm:w-[480px] dark:bg-[#0A0A0F]"
      >
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-white/10">
          <div class="flex items-center gap-2">
            <Sparkles class="h-5 w-5 text-primary" />
            <h2 class="text-lg font-bold text-slate-800 dark:text-white">AI 优化建议</h2>
          </div>

          <button
            class="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 dark:hover:bg-white/5"
            @click="close"
          >
            <X class="h-5 w-5" />
          </button>
        </div>

        <div class="custom-scroll flex-1 overflow-y-auto p-6">
          <div
            v-if="store.error"
            class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300"
          >
            {{ store.error }}
          </div>

          <div v-if="pendingSuggestions.length === 0 && !store.error" class="py-12 text-center">
            <Sparkles class="mx-auto mb-4 h-12 w-12 text-slate-300 dark:text-slate-600" />
            <p class="text-sm text-slate-500 dark:text-slate-400">
              AI 优化建议已经处理完成，当前没有待确认的修改项。
            </p>
          </div>

          <div v-else class="space-y-4">
            <article
              v-for="suggestion in pendingSuggestions"
              :key="suggestion.id"
              class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-white/5"
            >
              <div class="mb-3">
                <div class="mb-1 text-xs font-medium text-slate-500 dark:text-slate-400">原文</div>
                <div class="rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-600 dark:border-white/10 dark:bg-[#1a1a2e] dark:text-slate-300">
                  {{ suggestion.originalText }}
                </div>
              </div>

              <div class="mb-3">
                <div class="mb-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">AI 建议</div>
                <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-slate-700 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-slate-200">
                  {{ suggestion.suggestedText }}
                </div>
              </div>

              <div class="mb-4 flex items-start gap-1 text-xs text-slate-500 dark:text-slate-400">
                <span class="font-medium">理由：</span>
                <span>{{ suggestion.reason }}</span>
              </div>

              <div class="flex gap-2">
                <button
                  class="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-emerald-600"
                  @click="handleAccept(suggestion.id)"
                >
                  <Check class="h-4 w-4" />
                  接受
                </button>

                <button
                  class="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-300 dark:bg-white/10 dark:text-slate-300 dark:hover:bg-white/20"
                  @click="handleReject(suggestion.id)"
                >
                  <XCircle class="h-4 w-4" />
                  拒绝
                </button>
              </div>
            </article>
          </div>
        </div>
      </aside>
    </Transition>
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

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}
</style>
