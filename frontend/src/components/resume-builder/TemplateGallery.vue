<script setup lang="ts">
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import ResumeStylePanel from './ResumeStylePanel.vue'

const store = useResumeBuilderStore()
</script>

<template>
  <ResumeStylePanel
    :template-id="store.document.settings.templateId"
    :theme-color="store.document.settings.themeColor"
    :font-size="store.document.settings.fontSize"
    :line-height="store.document.settings.lineHeight"
    @update:template-id="(id) => store.setTemplate(id)"
    @update:theme-color="(c) => store.updateSettings({ themeColor: c })"
    @update:font-size="(v) => store.updateSettings({ fontSize: v })"
    @update:line-height="(v) => store.updateSettings({ lineHeight: v })"
  />
</template>
