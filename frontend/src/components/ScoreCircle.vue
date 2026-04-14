<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps<{ score: number }>()

const MAX_SCORE = 10
const dashArray = ref('0, 100')

const normalizedScore = computed(() => {
  const value = Number(props.score)
  if (!Number.isFinite(value)) return 0
  return Math.min(Math.max(value, 0), MAX_SCORE)
})

const progressPercent = computed(() => normalizedScore.value * 10)

function syncDashArray() {
  dashArray.value = `${progressPercent.value}, 100`
}

onMounted(() => {
  requestAnimationFrame(syncDashArray)
})

watch(progressPercent, syncDashArray)
</script>

<template>
  <div class="relative w-40 h-40 mb-4">
    <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
      <path class="text-slate-100 dark:text-slate-800" stroke-width="3" stroke="currentColor" fill="none"
        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
      <path class="text-primary transition-all duration-1000 ease-out" :stroke-dasharray="dashArray"
        stroke-width="3" stroke-linecap="round" stroke="currentColor" fill="none"
        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-5xl font-black text-slate-800 dark:text-white tracking-tighter">{{ normalizedScore }}</span>
    </div>
  </div>
</template>
