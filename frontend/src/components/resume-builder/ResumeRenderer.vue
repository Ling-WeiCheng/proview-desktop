<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import type { TemplateId, ResumeDocument } from '../../types/resume-builder'

const props = defineProps<{
  document?: ResumeDocument
}>()

const store = useResumeBuilderStore()

const doc = computed(() => props.document ?? store.document)

const templateComponents: Record<TemplateId, ReturnType<typeof defineAsyncComponent>> = {
  classic: defineAsyncComponent(() => import('./TemplateClassic.vue')),
  modern: defineAsyncComponent(() => import('./TemplateModern.vue')),
  minimal: defineAsyncComponent(() => import('./TemplateMinimal.vue')),
  fresh: defineAsyncComponent(() => import('./TemplateFresh.vue')),
  tech: defineAsyncComponent(() => import('./TemplateTech.vue')),
  creative: defineAsyncComponent(() => import('./TemplateCreative.vue')),
  executive: defineAsyncComponent(() => import('./TemplateExecutive.vue')),
  compact: defineAsyncComponent(() => import('./TemplateCompact.vue')),
  elegant: defineAsyncComponent(() => import('./TemplateElegant.vue')),
}

const currentTemplate = computed(() =>
  templateComponents[doc.value.settings.templateId] || templateComponents.classic
)
</script>

<template>
  <div class="resume-renderer">
    <component :is="currentTemplate" :document="doc" />
  </div>
</template>
