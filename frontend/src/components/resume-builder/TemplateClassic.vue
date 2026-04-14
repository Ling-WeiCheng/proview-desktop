<script setup lang="ts">
import { computed } from 'vue'
import type { ResumeDocument, ResumeModule, ModuleType } from '../../types/resume-builder'

const props = defineProps<{ document: ResumeDocument }>()

const visibleModules = computed(() =>
  [...props.document.modules].filter(m => m.visible).sort((a, b) => a.sortIndex - b.sortIndex),
)

const contactParts = computed(() => {
  const b = props.document.basicInfo
  return [b.mobile, b.email, b.location, b.workYears ? `${b.workYears}工作经验` : ''].filter(Boolean)
})

const showPhoto = computed(
  () => props.document.settings.photoShow && !!props.document.basicInfo.photoUrl,
)

const entryTypes: ModuleType[] = ['education', 'work', 'project', 'internship', 'campus']

function isEntryType(type: ModuleType) {
  return entryTypes.includes(type)
}

function formatTimeRange(start: string, end: string, isCurrent: boolean) {
  if (!start && !end) return ''
  const endText = isCurrent ? '至今' : end
  return `${start} - ${endText}`
}

function intentionLine(mod: ResumeModule) {
  if (!mod.intention) return ''
  const { targetJob, targetCity, salary, availableDate } = mod.intention
  return [targetJob, targetCity, salary, availableDate].filter(Boolean).join(' | ')
}

const cssVarColor = computed(() => props.document.settings.themeColor)
const cssVarFontSize = computed(() => `${props.document.settings.fontSize}px`)
const cssVarLineHeight = computed(() => String(props.document.settings.lineHeight))
const cssVarMargin = computed(() => `${props.document.settings.marginMm}mm`)

const intentionModule = computed(() =>
  props.document.modules.find(m => m.type === 'intention' && m.visible && intentionLine(m))
)
</script>

<template>
  <div class="classic-page">
    <!-- Header -->
    <header class="header">
      <div class="header-text">
        <h1 class="name">{{ document.basicInfo.name }}</h1>
        <p v-if="contactParts.length" class="contact-line">
          <span v-for="(part, i) in contactParts" :key="i">
            <span v-if="i > 0" class="sep">|</span>{{ part }}
          </span>
        </p>
        <!-- intention 提升到 header 内，填充照片旁空白 -->
        <p v-if="intentionModule" class="intention-inline">
          求职意向：{{ intentionLine(intentionModule) }}
        </p>
      </div>
      <img v-if="showPhoto" :src="document.basicInfo.photoUrl" class="photo" alt="照片" />
    </header>

    <!-- Modules -->
    <section v-for="mod in visibleModules" :key="mod.id" class="module">
      <!-- Intention already shown in header, skip here -->
      <template v-if="mod.type === 'intention'" />

      <!-- All other modules -->
      <template v-else>
        <h2 class="section-title">{{ mod.title }}</h2>

        <!-- Entry-based modules -->
        <template v-if="isEntryType(mod.type) && mod.entries?.length">
          <div v-for="entry in mod.entries" :key="entry.id" class="entry">
            <div class="entry-head">
              <span class="entry-org">{{ entry.orgName }}</span>
              <span v-if="entry.role" class="entry-role">{{ entry.role }}</span>
              <span class="entry-time">
                {{ formatTimeRange(entry.timeStart, entry.timeEnd, entry.isCurrent) }}
              </span>
            </div>
            <div v-if="entry.detail" class="entry-detail" v-html="entry.detail" />
          </div>
        </template>

        <!-- Skills -->
        <template v-if="mod.type === 'skills'">
          <div v-if="mod.content" class="text-content" v-html="mod.content" />
        </template>

        <!-- Hobbies (tags) -->
        <template v-if="mod.type === 'hobbies'">
          <div v-if="mod.tags?.length" class="hobby-tags">
            <span v-for="(tag, i) in mod.tags" :key="i" class="hobby-pill">{{ tag }}</span>
          </div>
          <div v-else-if="mod.content" class="text-content" v-html="mod.content" />
        </template>

        <!-- Text-only modules -->
        <template v-if="['certificates', 'evaluation', 'custom'].includes(mod.type)">
          <div v-if="mod.content" class="text-content" v-html="mod.content" />
        </template>
      </template>
    </section>
  </div>
</template>

<style scoped>
/* --- Page --- */
.classic-page {
  --resume-color: v-bind(cssVarColor);
  --resume-font-size: v-bind(cssVarFontSize);
  --resume-line-height: v-bind(cssVarLineHeight);
  --resume-margin: v-bind(cssVarMargin);

  width: 794px;
  min-height: 1123px;
  background: #fff;
  color: #333;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: var(--resume-font-size);
  line-height: var(--resume-line-height);
  padding: 25px var(--resume-margin);
  box-sizing: border-box;
  overflow: hidden;
}

/* --- Photo --- */
.photo {
  width: 90px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

/* --- Header --- */
.header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 6px;
}

.header-text {
  text-align: center;
  flex: 1;
}

.name {
  font-size: 23px;
  font-weight: 700;
  letter-spacing: 2px;
  margin: 0 0 6px;
  color: #222;
}

.contact-line {
  font-size: 12.5px;
  color: #555;
  margin: 0;
}

.sep {
  margin: 0 8px;
  color: #ccc;
}

/* --- Intention --- */
.intention-inline {
  text-align: center;
  font-size: 12.5px;
  color: #555;
  margin: 5px 0 0;
}

/* --- Section --- */
.module {
  margin-top: 18px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--resume-color);
  margin: 0 0 8px;
  padding-bottom: 4px;
  border-bottom: 2px solid var(--resume-color);
  letter-spacing: 0.5px;
}

/* --- Entry --- */
.entry {
  margin-bottom: 10px;
}

.entry-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 3px;
}

.entry-org {
  font-weight: 600;
  color: #222;
}

.entry-role {
  color: #444;
}

.entry-time {
  margin-left: auto;
  flex-shrink: 0;
  font-size: 12.5px;
  color: #888;
}

.entry-detail {
  color: #555;
  line-height: var(--resume-line-height);
  word-break: break-word;
  font-size: var(--resume-font-size);
}

.entry-detail :deep(p) { margin: 2px 0; }
.entry-detail :deep(ul), .entry-detail :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.entry-detail :deep(li) { margin: 1px 0; }
.entry-detail :deep(li > p) { margin: 0; }
.entry-detail :deep(strong) { font-weight: 600; color: #333; }

.entry-detail :deep(a) {
  color: var(--resume-color);
  text-decoration: none;
}

/* --- Skills --- */
.skill-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 6px;
}

.skill-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.skill-name {
  width: 80px;
  flex-shrink: 0;
  font-size: 12.5px;
  color: #444;
  text-align: right;
}

.skill-track {
  flex: 1;
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.skill-fill {
  height: 100%;
  background: var(--resume-color);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* --- Hobbies --- */
.hobby-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.hobby-pill {
  display: inline-block;
  padding: 3px 14px;
  font-size: 12px;
  color: var(--resume-color);
  border: 1px solid var(--resume-color);
  border-radius: 999px;
  line-height: 1.6;
}

/* --- Text content --- */
.text-content {
  color: #555;
  line-height: var(--resume-line-height);
  word-break: break-word;
}

.text-content :deep(a) { color: var(--resume-color); text-decoration: none; }
.text-content :deep(p) { margin: 2px 0; }
.text-content :deep(ul), .text-content :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.text-content :deep(li) { margin: 1px 0; }
.text-content :deep(li > p) { margin: 0; }
</style>
