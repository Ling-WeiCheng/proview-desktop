<script setup lang="ts">
import { computed } from 'vue'
import type { ResumeDocument, ModuleType } from '../../types/resume-builder'

const props = defineProps<{ document: ResumeDocument }>()

const visibleModules = computed(() =>
  [...props.document.modules].filter(m => m.visible).sort((a, b) => a.sortIndex - b.sortIndex)
)

const entryTypes: ModuleType[] = ['education', 'work', 'project', 'internship', 'campus']
const sidebarTypes: ModuleType[] = ['skills', 'hobbies', 'certificates']

const sidebarModules = computed(() => visibleModules.value.filter(m =>
  sidebarTypes.includes(m.type) || m.type === 'intention'
))
const mainModules = computed(() => visibleModules.value.filter(m =>
  !sidebarTypes.includes(m.type) && m.type !== 'intention'
))

const contactParts = computed(() => {
  const b = props.document.basicInfo
  return [
    { label: '电话', value: b.mobile },
    { label: '邮箱', value: b.email },
    { label: '所在地', value: b.location },
  ].filter(p => p.value)
})

function formatTime(start: string, end: string, cur: boolean) {
  if (!start && !end) return ''
  return `${start} - ${cur ? '至今' : end}`
}

function intentionLine(mod: any) {
  if (!mod.intention) return ''
  const { targetJob, targetCity, salary } = mod.intention
  return [targetJob, targetCity, salary].filter(Boolean).join(' · ')
}

const cssColor = computed(() => props.document.settings.themeColor)
const cssFontSize = computed(() => `${props.document.settings.fontSize}px`)
const cssLineHeight = computed(() => String(props.document.settings.lineHeight))
</script>

<template>
  <div class="creative-page">
    <!-- Left sidebar -->
    <aside class="sidebar">
      <div class="sidebar-inner">
        <!-- Photo / Initial -->
        <div class="photo-area">
          <div v-if="document.settings.photoShow && document.basicInfo.photoUrl" class="photo-wrap">
            <img :src="document.basicInfo.photoUrl" class="photo" alt="" />
          </div>
          <div v-else class="photo-initial">
            {{ document.basicInfo.name?.charAt(0) || '?' }}
          </div>
        </div>

        <!-- Contact -->
        <div v-if="contactParts.length" class="side-section">
          <h3 class="side-title">联系方式</h3>
          <p v-for="(c, i) in contactParts" :key="i" class="contact-line">{{ c.value }}</p>
        </div>

        <!-- Sidebar modules -->
        <template v-for="mod in sidebarModules">
          <div v-if="mod.type === 'intention' && mod.intention" :key="'i-' + mod.id" class="side-section">
            <h3 class="side-title">求职意向</h3>
            <p class="side-text">{{ intentionLine(mod) }}</p>
          </div>
          <div v-if="mod.type === 'skills'" :key="'s-' + mod.id" class="side-section">
            <h3 class="side-title">{{ mod.title }}</h3>
            <div v-if="mod.content" class="side-text" v-html="mod.content" />
          </div>
          <div v-if="mod.type === 'hobbies'" :key="'h-' + mod.id" class="side-section">
            <h3 class="side-title">{{ mod.title }}</h3>
            <div v-if="mod.tags?.length" class="hobby-tags">
              <span v-for="(t, i) in mod.tags" :key="i" class="hobby-pill">{{ t }}</span>
            </div>
            <div v-else-if="mod.content" class="side-text" v-html="mod.content" />
          </div>
          <div v-if="mod.type === 'certificates'" :key="'c-' + mod.id" class="side-section">
            <h3 class="side-title">{{ mod.title }}</h3>
            <div v-if="mod.content" class="side-text" v-html="mod.content" />
          </div>
        </template>
      </div>
    </aside>

    <!-- Right main area -->
    <main class="main-area">
      <h1 class="name">{{ document.basicInfo.name }}</h1>
      <p v-if="document.basicInfo.workYears" class="subtitle">{{ document.basicInfo.workYears }}工作经验</p>

      <section v-for="mod in mainModules" :key="mod.id" class="mod-section">
        <h2 class="mod-title">{{ mod.title }}</h2>
        <template v-if="entryTypes.includes(mod.type) && mod.entries?.length">
          <div v-for="entry in mod.entries" :key="entry.id" class="entry">
            <div class="entry-head">
              <span class="entry-org">{{ entry.orgName }}</span>
              <span v-if="entry.role" class="entry-role">{{ entry.role }}</span>
              <span class="entry-time">{{ formatTime(entry.timeStart, entry.timeEnd, entry.isCurrent) }}</span>
            </div>
            <div v-if="entry.detail" class="entry-detail" v-html="entry.detail" />
          </div>
        </template>
        <div v-else-if="mod.content" class="text-content" v-html="mod.content" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.creative-page {
  --mc: v-bind(cssColor);
  --fs: v-bind(cssFontSize);
  --lh: v-bind(cssLineHeight);
  display: flex;
  width: 794px;
  min-height: 1123px;
  background: #fff;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: var(--fs);
  line-height: var(--lh);
  color: #333;
  box-sizing: border-box;
  overflow: hidden;
}

/* ---- Sidebar ---- */
.sidebar {
  width: 200px;
  flex-shrink: 0;
  background: var(--mc);
  position: relative;
  overflow: hidden;
}
.sidebar::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.25) 100%);
  pointer-events: none;
}
.sidebar-inner {
  position: relative;
  z-index: 1;
  padding: 28px 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  color: #fff;
}

/* Photo */
.photo-area { text-align: center; }
.photo-wrap { display: inline-block; }
.photo {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
}
.photo-initial {
  width: 100px;
  height: 100px;
  margin: 0 auto;
  border-radius: 50%;
  border: 3px solid #fff;
  background: rgba(255,255,255,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: #fff;
}

/* Sidebar sections */
.side-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin: 0 0 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(255,255,255,0.3);
}
.contact-line { font-size: 12px; margin: 3px 0; opacity: 0.9; word-break: break-all; }
.side-text { font-size: 12px; opacity: 0.9; white-space: pre-wrap; }
.side-text :deep(a) { color: #fff; }

/* Skills */
.skill-bars { display: flex; flex-direction: column; gap: 7px; }
.skill-name { font-size: 11.5px; }
.skill-track { height: 5px; background: rgba(255,255,255,0.2); border-radius: 3px; margin-top: 2px; overflow: hidden; }
.skill-fill { height: 100%; background: #fff; border-radius: 3px; }

/* Hobbies */
.hobby-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.hobby-pill { font-size: 11px; padding: 2px 9px; border: 1px solid rgba(255,255,255,0.5); border-radius: 999px; }

/* ---- Main area ---- */
.main-area { flex: 1; padding: 28px 30px; }
.name { font-size: 24px; font-weight: 700; margin: 0 0 2px; color: var(--mc); }
.subtitle { font-size: 13px; color: #888; margin: 0 0 16px; }

.mod-section { margin-top: 18px; }
.mod-title {
  font-size: 15px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px;
  padding-left: 10px;
  border-left: 4px solid var(--mc);
}

.entry { margin-bottom: 10px; }
.entry-head { display: flex; align-items: baseline; gap: 6px; margin-bottom: 2px; }
.entry-org { font-weight: 600; color: #222; }
.entry-role { color: #555; }
.entry-time { margin-left: auto; font-size: 12px; color: #999; flex-shrink: 0; }
.entry-detail { color: #555; word-break: break-word; }
.entry-detail :deep(a) { color: var(--mc); }
.entry-detail :deep(p) { margin: 2px 0; }
.entry-detail :deep(ul), .entry-detail :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.entry-detail :deep(li) { margin: 1px 0; }
.entry-detail :deep(li > p) { margin: 0; }
.text-content { color: #555; word-break: break-word; }
.text-content :deep(a) { color: var(--mc); }
.text-content :deep(p) { margin: 2px 0; }
.text-content :deep(ul), .text-content :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.text-content :deep(li) { margin: 1px 0; }
.text-content :deep(li > p) { margin: 0; }
</style>
