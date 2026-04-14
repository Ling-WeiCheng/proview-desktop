<script setup lang="ts">
import { ref, computed } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import { User, Camera, Trash2 } from 'lucide-vue-next'

const store = useResumeBuilderStore()
const info = computed(() => store.document.basicInfo)
const fileInput = ref<HTMLInputElement | null>(null)

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    store.updateBasicInfo({ photoUrl: reader.result as string })
  }
  reader.readAsDataURL(file)
}

function removePhoto() {
  store.updateBasicInfo({ photoUrl: '' })
}

const inputClass = 'w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-indigo-500/20 dark:border-white/10 dark:bg-[#1a1a2e] dark:text-slate-200'
const labelClass = 'block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1'
</script>

<template>
  <div class="border border-slate-200/80 dark:border-white/5 rounded-2xl overflow-hidden">
    <div class="flex items-center gap-2 px-4 py-3 bg-slate-50/80 dark:bg-white/[0.02] border-b border-slate-100 dark:border-white/5">
      <User class="w-4 h-4 text-primary" />
      <span class="text-sm font-bold text-slate-700 dark:text-slate-200">个人信息</span>
    </div>
    <div class="p-4 space-y-4">
      <!-- Photo upload -->
      <div class="flex items-center gap-4">
        <div
          class="relative w-16 h-20 rounded-lg overflow-hidden border-2 border-dashed border-slate-300 dark:border-white/15 flex items-center justify-center cursor-pointer hover:border-primary transition-colors group"
          @click="triggerUpload"
        >
          <img v-if="info.photoUrl" :src="info.photoUrl" class="w-full h-full object-cover" alt="" />
          <Camera v-else class="w-5 h-5 text-slate-400 group-hover:text-primary transition-colors" />
        </div>
        <div class="flex-1 space-y-1">
          <div class="text-xs font-medium text-slate-500 dark:text-slate-400">证件照</div>
          <div class="flex gap-2">
            <button
              @click="triggerUpload"
              class="text-xs px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5 transition-colors"
            >上传照片</button>
            <button
              v-if="info.photoUrl"
              @click="removePhoto"
              class="text-xs px-2 py-1.5 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
            ><Trash2 class="w-3.5 h-3.5" /></button>
          </div>
          <div class="text-[11px] text-slate-400 dark:text-slate-500">建议尺寸 295×413，支持 JPG/PNG</div>
        </div>
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFileChange" />
      </div>

      <!-- Form fields -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3">
        <div>
          <label :class="labelClass">姓名</label>
          <input v-model="info.name" placeholder="请输入姓名" :class="inputClass" />
        </div>
        <div>
          <label :class="labelClass">性别</label>
          <select v-model="info.gender" :class="inputClass">
            <option value="">不填</option>
            <option value="男">男</option>
            <option value="女">女</option>
          </select>
        </div>
        <div>
          <label :class="labelClass">出生年月</label>
          <input v-model="info.birthday" type="month" :class="inputClass" />
        </div>
        <div>
          <label :class="labelClass">手机号</label>
          <input v-model="info.mobile" type="tel" placeholder="请输入手机号" :class="inputClass" />
        </div>
        <div>
          <label :class="labelClass">邮箱</label>
          <input v-model="info.email" type="email" placeholder="请输入邮箱" :class="inputClass" />
        </div>
        <div>
          <label :class="labelClass">所在城市</label>
          <input v-model="info.location" placeholder="如：上海" :class="inputClass" />
        </div>
        <div>
          <label :class="labelClass">工作年限</label>
          <input v-model="info.workYears" placeholder="如：3年经验" :class="inputClass" />
        </div>
      </div>
    </div>
  </div>
</template>
