<script setup lang="ts">
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import ModuleFormCard from './ModuleFormCard.vue'
import AddModuleButton from './AddModuleButton.vue'

const store = useResumeBuilderStore()
</script>

<template>
  <div class="space-y-3">
    <ModuleFormCard
      v-for="mod in store.sortedModules"
      :key="mod.id"
      :module-id="mod.id"
    />
    <AddModuleButton />
  </div>
</template>
