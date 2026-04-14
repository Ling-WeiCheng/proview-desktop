<script setup lang="ts">
import { computed } from 'vue'
import { Eye, EyeOff, Trash2, ChevronDown, ChevronUp } from 'lucide-vue-next'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import IntentionForm from './IntentionForm.vue'
import TimeRangeForm from './TimeRangeForm.vue'
import SkillsForm from './SkillsForm.vue'
import RichTextForm from './RichTextForm.vue'

const props = defineProps<{ moduleId: string }>()
const store = useResumeBuilderStore()

const mod = computed(() => store.document.modules.find(m => m.id === props.moduleId))

const isExpanded = computed(() => store.activeModuleId === props.moduleId)

function toggle() {
  store.activeModuleId = isExpanded.value ? null : props.moduleId
}

const timeRangeTypes = ['education', 'work', 'project', 'internship', 'campus']

const formComponent = computed(() => {
  if (!mod.value) return null
  const t = mod.value.type
  if (t === 'intention') return IntentionForm
  if (timeRangeTypes.includes(t)) return TimeRangeForm
  if (t === 'skills') return SkillsForm
  return RichTextForm
})
</script>

<template>
  <div
    v-if="mod"
    class="border border-slate-200/80 dark:border-white/5 rounded-2xl overflow-hidden transition-all"
  >
    <!-- Header -->
    <div
      class="flex items-center gap-2 px-4 py-3 cursor-pointer hover:bg-slate-50 dark:hover:bg-white/5"
      @click="toggle"
    >
      <!-- Editable title -->
      <input
        type="text"
        v-model="mod.title"
        class="text-sm font-medium text-slate-700 dark:text-slate-200 bg-transparent outline-none flex-1 min-w-0"
        @click.stop
      />

      <!-- Visibility toggle -->
      <button
        class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition"
        @click.stop="store.toggleModuleVisibility(props.moduleId)"
      >
        <Eye v-if="mod.visible" class="w-4 h-4" />
        <EyeOff v-else class="w-4 h-4" />
      </button>

      <!-- Delete -->
      <button
        class="p-1 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
        @click.stop="store.removeModule(props.moduleId)"
      >
        <Trash2 class="w-4 h-4" />
      </button>

      <!-- Expand/Collapse indicator -->
      <component :is="isExpanded ? ChevronUp : ChevronDown" class="w-4 h-4 text-slate-400 shrink-0" />
    </div>

    <!-- Body -->
    <div v-show="isExpanded" class="px-4 pb-4">
      <component :is="formComponent" :module-id="props.moduleId" />
    </div>
  </div>
</template>
