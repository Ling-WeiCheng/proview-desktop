<script setup lang="ts">
import { computed } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import type { JobIntention } from '../../types/resume-builder'

const props = defineProps<{ moduleId: string }>()
const store = useResumeBuilderStore()

const intention = computed(() => {
  const mod = store.document.modules.find(m => m.id === props.moduleId)
  if (!mod?.intention) return { targetJob: '', targetCity: '', salary: '', availableDate: '' } as JobIntention
  return mod.intention
})

const inputCls = 'w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-indigo-500/20 dark:border-white/10 dark:bg-white/5'
const labelCls = 'block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1'
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
    <div>
      <label :class="labelCls">目标岗位</label>
      <input type="text" :class="inputCls" v-model="intention.targetJob" placeholder="如：前端工程师" />
    </div>
    <div>
      <label :class="labelCls">目标城市</label>
      <input type="text" :class="inputCls" v-model="intention.targetCity" placeholder="如：北京" />
    </div>
    <div>
      <label :class="labelCls">期望薪资</label>
      <input type="text" :class="inputCls" v-model="intention.salary" placeholder="如：15-20K" />
    </div>
    <div>
      <label :class="labelCls">到岗时间</label>
      <input type="text" :class="inputCls" v-model="intention.availableDate" placeholder="如：随时到岗" />
    </div>
  </div>
</template>
