<script setup lang="ts">
defineProps<{ text: string }>()
</script>

<template>
  <div class="flex justify-center fade-in my-3">
    <span class="bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-300 text-xs px-3 py-1.5 rounded-full border border-indigo-100 dark:border-indigo-500/30 font-medium">
      {{ text }}
    </span>
  </div>
</template>
