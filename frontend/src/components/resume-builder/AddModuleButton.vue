<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import { MODULE_TYPE_META } from '../../types/resume-builder'
import type { ModuleType } from '../../types/resume-builder'

const store = useResumeBuilderStore()
const open = ref(false)

const moduleTypes = Object.entries(MODULE_TYPE_META) as [ModuleType, (typeof MODULE_TYPE_META)[ModuleType]][]

function select(type: ModuleType) {
  store.addModule(type)
  open.value = false
}
</script>

<template>
  <div class="relative">
    <button
      class="flex items-center gap-1.5 text-sm text-primary hover:text-primary/80 transition px-3 py-2 rounded-xl border border-dashed border-slate-300 dark:border-white/10 hover:border-primary dark:hover:border-primary/50 w-full justify-center"
      @click="open = !open"
    >
      <Plus class="w-4 h-4" />
      <span>添加模块</span>
    </button>

    <!-- Dropdown -->
    <div
      v-if="open"
      class="absolute left-0 right-0 mt-1 z-20 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 shadow-lg py-1 max-h-64 overflow-y-auto"
    >
      <button
        v-for="[type, meta] in moduleTypes"
        :key="type"
        class="w-full text-left px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5 transition"
        @click="select(type)"
      >
        {{ meta.label }}
      </button>
    </div>

    <!-- Backdrop to close dropdown -->
    <div
      v-if="open"
      class="fixed inset-0 z-10"
      @click="open = false"
    />
  </div>
</template>
