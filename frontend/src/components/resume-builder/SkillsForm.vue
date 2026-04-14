<script setup lang="ts">
import { computed } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'

const props = defineProps<{ moduleId: string }>()
const store = useResumeBuilderStore()

const mod = computed(() => store.document.modules.find(m => m.id === props.moduleId))

const inputCls = 'w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-indigo-500/20 dark:border-white/10 dark:bg-white/5'
const labelCls = 'block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1'
</script>

<template>
  <div class="space-y-4">
    <!-- Rich text area for skill description -->
    <div>
      <label :class="labelCls">技能描述</label>
      <textarea
        v-if="mod"
        :class="inputCls"
        v-model="mod.content"
        rows="6"
        placeholder="概述你的技能特长，如：熟练掌握 Vue 3、React 等前端框架..."
      />
    </div>
  </div>
</template>
