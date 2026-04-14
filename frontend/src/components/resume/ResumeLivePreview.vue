<script setup lang="ts">
import { computed } from 'vue'
import 'katex/dist/katex.min.css'
import { useResumeStore } from '../../stores/resume'
import ResumeRenderer from '../resume-builder/ResumeRenderer.vue'
import { renderContent } from '../../utils/renderContent'

const store = useResumeStore()
const emit = defineEmits<{
  openFullscreen: []
}>()

const sectionTypeLabel: Record<string, string> = {
  personal_info: '个人信息',
  education: '教育背景',
  experience: '工作经历',
  skills: '技能特长',
  projects: '项目经历',
  certifications: '证书资质',
  other: '其他'
}

// 将 sections 渲染为类似真实简历的 HTML
const resumeHtml = computed(() => {
  if (store.sections.length === 0) return ''
  const parts: string[] = []

  for (const sec of store.sections) {
    const label = sectionTypeLabel[sec.type] || sec.type
    const contentHtml = renderContent(sec.content)

    if (sec.type === 'personal_info') {
      const nameText = sec.title.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      const initial = sec.title.charAt(0) || '?'
      const avatarKeys = Object.keys(store.images)
      const avatarSrc = avatarKeys.reduce((found, key) => {
        if (found) return found
        const val = store.images[key]
        if (val && (val.startsWith('data:image') || val.startsWith('http'))) return val
        return ''
      }, '')
      const avatarHtml = avatarSrc
        ? `<img src="${avatarSrc}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;flex-shrink:0;" />`
        : `<div style="width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#4F46E5,#7C3AED);display:flex;align-items:center;justify-content:center;color:white;font-size:24px;font-weight:800;flex-shrink:0;">${initial}</div>`
      parts.push(`
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid #4F46E5;">
          ${avatarHtml}
          <div>
            <div style="font-size:22px;font-weight:800;color:#1e293b;">${nameText}</div>
            <div style="margin-top:4px;color:#64748b;font-size:12px;">${contentHtml}</div>
          </div>
        </div>
      `)
    } else {
      parts.push(`
        <div style="margin-bottom:16px;">
          <div style="font-size:14px;font-weight:700;color:#4F46E5;border-bottom:1px solid #e2e8f0;padding-bottom:4px;margin-bottom:8px;">
            ${sec.title || label}
          </div>
          <div class="section-content">${contentHtml}</div>
        </div>
      `)
    }
  }

  return parts.join('')
})
</script>

<template>
  <div class="resume-live-preview">
    <div v-if="store.sections.length === 0" class="text-center py-10 text-slate-400 text-sm">
      暂无简历内容
    </div>

    <!-- 模板渲染模式 -->
    <div
      v-else-if="store.builderDocument"
      class="template-preview-wrapper"
      role="button"
      tabindex="0"
      @click="emit('openFullscreen')"
      @keydown.enter.prevent="emit('openFullscreen')"
      @keydown.space.prevent="emit('openFullscreen')"
    >
      <div class="preview-click-hint">点击预览可放大查看</div>
      <div class="template-scaler">
        <ResumeRenderer :document="store.builderDocument" />
      </div>
    </div>

    <!-- Fallback: 原始 markdown 渲染 -->
    <div v-else class="resume-paper">
      <div v-html="resumeHtml" />
    </div>
  </div>
</template>

<style scoped>
.template-preview-wrapper {
  position: relative;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
  overflow: hidden;
  width: 100%;
  cursor: zoom-in;
  transition: box-shadow 0.18s ease, transform 0.18s ease;
}

.template-preview-wrapper:hover,
.template-preview-wrapper:focus-visible {
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12), 0 0 0 1px rgba(79, 70, 229, 0.2);
  outline: none;
}

.preview-click-hint {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.72);
  color: white;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  pointer-events: none;
  backdrop-filter: blur(8px);
}

/* 内部固定 794px 的模板，用 zoom 缩放到容器宽度 */
.template-scaler {
  width: 794px;
  zoom: calc(1 / (794 / 100%));
  transform-origin: top left;
}

:root.dark .template-preview-wrapper,
.dark .template-preview-wrapper {
  box-shadow: 0 1px 4px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05);
}

:root.dark .template-preview-wrapper:hover,
:root.dark .template-preview-wrapper:focus-visible,
.dark .template-preview-wrapper:hover,
.dark .template-preview-wrapper:focus-visible {
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.5), 0 0 0 1px rgba(129, 140, 248, 0.32);
}

:root.dark .preview-click-hint,
.dark .preview-click-hint {
  background: rgba(15, 23, 42, 0.78);
  color: rgba(226, 232, 240, 0.96);
}

.resume-paper {
  background: white;
  border-radius: 8px;
  padding: 32px 28px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  color: #1e293b;
  line-height: 1.7;
  font-size: 13px;
}

/* markdown 渲染内容样式（v-html 需要 :deep） */
.resume-paper :deep(h2) { font-size: 13px; font-weight: 700; color: #4F46E5; margin: 12px 0 6px; }
.resume-paper :deep(h3) { font-size: 12px; font-weight: 700; color: #334155; margin: 8px 0 4px; }
.resume-paper :deep(p) { margin: 3px 0; }
.resume-paper :deep(ul),
.resume-paper :deep(ol) { margin: 3px 0 3px 18px; padding: 0; }
.resume-paper :deep(li) { margin: 1.5px 0; }
.resume-paper :deep(li > p) { margin: 0; }
.resume-paper :deep(a) { color: #4F46E5; text-decoration: none; }
.resume-paper :deep(strong) { font-weight: 700; }
.resume-paper :deep(hr) { border: none; border-top: 1px solid #e2e8f0; margin: 10px 0; }
.resume-paper :deep(code) { background: #f1f5f9; padding: 1px 3px; border-radius: 2px; font-size: 11px; }
.resume-paper :deep(table) { width: 100%; border-collapse: collapse; margin: 6px 0; font-size: 12px; }
.resume-paper :deep(th),
.resume-paper :deep(td) { border: 1px solid #e2e8f0; padding: 4px 8px; text-align: left; }
.resume-paper :deep(th) { background: #f1f5f9; font-weight: 700; }

.section-content { color: #334155; }

:root.dark .resume-paper,
.dark .resume-paper {
  background: #0f0f1a;
  color: #cbd5e1;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.05);
}
:root.dark .resume-paper :deep(h3),
.dark .resume-paper :deep(h3) { color: #94a3b8; }
:root.dark .resume-paper :deep(a),
.dark .resume-paper :deep(a) { color: #818cf8; }
:root.dark .resume-paper :deep(code),
.dark .resume-paper :deep(code) { background: #1e1e2e; }
:root.dark .section-content,
.dark .section-content { color: #cbd5e1; }
</style>
