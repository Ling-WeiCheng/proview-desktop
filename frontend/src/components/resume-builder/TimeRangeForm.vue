<script setup lang="ts">
import { computed } from 'vue'
import { X, Plus } from 'lucide-vue-next'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'

const props = defineProps<{ moduleId: string }>()
const store = useResumeBuilderStore()

const mod = computed(() => store.document.modules.find(m => m.id === props.moduleId))
const entries = computed(() => mod.value?.entries ?? [])

const inputCls = 'w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-indigo-500/20 dark:border-white/10 dark:bg-white/5'
const labelCls = 'block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1'
</script>

<template>
  <div>
    <div
      v-for="entry in entries"
      :key="entry.id"
      class="border border-slate-100 dark:border-white/5 rounded-xl p-3 mb-3 relative"
    >
      <!-- Delete button -->
      <button
        class="absolute top-2 right-2 p-1 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
        @click="store.removeEntry(props.moduleId, entry.id)"
      >
        <X class="w-4 h-4" />
      </button>

      <!-- Row 1: 机构名称 -->
      <div class="mb-3">
        <label :class="labelCls">机构名称</label>
        <input type="text" :class="inputCls" v-model="entry.orgName" placeholder="公司/学校/组织名称" />
      </div>

      <!-- Row 2: 角色 + 时间范围 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
        <div>
          <label :class="labelCls">角色/专业</label>
          <input type="text" :class="inputCls" v-model="entry.role" placeholder="职位/专业名称" />
        </div>
        <div>
          <label :class="labelCls">时间范围</label>
          <div class="flex items-center gap-2">
            <input type="month" :class="inputCls" v-model="entry.timeStart" />
            <span class="text-slate-400 text-xs shrink-0">—</span>
            <input
              v-if="!entry.isCurrent"
              type="month"
              :class="inputCls"
              v-model="entry.timeEnd"
            />
            <span v-else class="text-xs text-primary font-medium shrink-0">至今</span>
            <label class="flex items-center gap-1 shrink-0 cursor-pointer">
              <input type="checkbox" v-model="entry.isCurrent" class="rounded" />
              <span class="text-xs text-slate-500 dark:text-slate-400">至今</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Row 3: 详细描述 -->
      <div>
        <label :class="labelCls">详细描述</label>
        <textarea
          :class="inputCls"
          v-model="entry.detail"
          rows="4"
          placeholder="描述你的工作内容、成果、技术栈等"
        />
      </div>
    </div>

    <!-- Add button -->
    <button
      class="flex items-center gap-1.5 text-sm text-primary hover:text-primary/80 transition px-2 py-1.5 rounded-lg hover:bg-primary/5"
      @click="store.addEntry(props.moduleId)"
    >
      <Plus class="w-4 h-4" />
      <span>添加</span>
    </button>
  </div>
</template>
