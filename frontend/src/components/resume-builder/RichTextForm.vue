<script setup lang="ts">
import { computed } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'

const props = defineProps<{ moduleId: string }>()
const store = useResumeBuilderStore()

const mod = computed(() => store.document.modules.find(m => m.id === props.moduleId))

const inputCls = 'w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-indigo-500/20 dark:border-white/10 dark:bg-white/5'
</script>

<template>
  <div>
    <textarea
      v-if="mod"
      :class="inputCls"
      v-model="mod.content"
      rows="6"
      placeholder="请输入内容..."
    />
  </div>
</template>
