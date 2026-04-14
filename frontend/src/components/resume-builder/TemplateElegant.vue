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

const cssColor = computed(() => props.document.settings.themeColor)
const cssFontSize = computed(() => `${props.document.settings.fontSize}px`)
const cssLineHeight = computed(() => String(props.document.settings.lineHeight))
</script>

<template>
  <div class="elegant-page">
    <!-- Photo -->
    <img
      v-if="showPhoto"
      :src="document.basicInfo.photoUrl"
      class="photo"
      alt="照片"
    />

    <!-- Header -->
    <header class="header">
      <h1 class="name">{{ document.basicInfo.name }}</h1>
      <div class="header-line" />
      <p v-if="contactParts.length" class="contact-line">
        <span v-for="(part, i) in contactParts" :key="i">
          <span v-if="i > 0" class="sep">|</span>{{ part }}
        </span>
      </p>
    </header>

    <!-- Modules -->
    <section v-for="mod in visibleModules" :key="mod.id" class="module">
      <!-- Intention -->
      <template v-if="mod.type === 'intention'">
        <p v-if="intentionLine(mod)" class="intention-line">
          {{ intentionLine(mod) }}
        </p>
      </template>

      <!-- All other modules -->
      <template v-else>
        <h2 class="section-title">
          <span class="section-title-text">{{ mod.title }}</span>
        </h2>

        <!-- Entry-based modules (timeline) -->
        <template v-if="isEntryType(mod.type) && mod.entries?.length">
          <div class="timeline">
            <div v-for="entry in mod.entries" :key="entry.id" class="timeline-item">
              <div class="timeline-track">
                <span class="timeline-dot" />
                <span class="timeline-line" />
              </div>
              <div class="timeline-content">
                <div class="entry-head">
                  <span class="entry-org">{{ entry.orgName }}</span>
                  <span v-if="entry.role" class="entry-role">{{ entry.role }}</span>
                  <span class="entry-time">
                    {{ formatTimeRange(entry.timeStart, entry.timeEnd, entry.isCurrent) }}
                  </span>
                </div>
                <div v-if="entry.detail" class="entry-detail" v-html="entry.detail" />
              </div>
            </div>
          </div>
        </template>

        <!-- Skills -->
        <template v-if="mod.type === 'skills'">
          <div v-if="mod.content" class="text-content" v-html="mod.content" />
        </template>

        <!-- Hobbies -->
        <template v-if="mod.type === 'hobbies'">
          <p v-if="mod.tags?.length" class="hobby-list">
            {{ mod.tags.join('，') }}
          </p>
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
.elegant-page {
  --mc: v-bind(cssColor);
  --fs: v-bind(cssFontSize);
  --lh: v-bind(cssLineHeight);
  position: relative;
  width: 794px;
  min-height: 1123px;
  background: #fff;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: var(--fs);
  line-height: var(--lh);
  color: #333;
  box-sizing: border-box;
  overflow: hidden;
  padding: 40px 50px;
}

/* --- Photo --- */
.photo {
  position: absolute;
  top: 40px;
  right: 50px;
  width: 80px;
  height: 100px;
  object-fit: cover;
  border-radius: 50%;
  border: 1.5px solid var(--mc);
}

/* --- Header --- */
.header {
  text-align: center;
  margin-bottom: 8px;
}

.header {
  text-align: center;
  margin-bottom: 8px;
}

.name {
  font-family: "Georgia", "Times New Roman", "SimSun", serif;
  font-size: 28px;
  font-weight: 400;
  letter-spacing: 2px;
  color: var(--mc);
  margin: 0 0 10px;
}

.header-line {
  width: 100%;
  height: 1px;
  background: var(--mc);
  margin-bottom: 8px;
}

.contact-line {
  font-family: "Georgia", "Times New Roman", "SimSun", serif;
  font-size: 12px;
  color: #666;
  margin: 0;
}

.sep {
  margin: 0 10px;
  color: #ccc;
}

/* --- Intention --- */
.intention-line {
  text-align: center;
  font-family: "Georgia", "Times New Roman", "SimSun", serif;
  font-style: italic;
  font-size: 13px;
  color: #666;
  margin: 6px 0 0;
}

/* --- Section --- */
.module {
  margin-top: 22px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: "Georgia", "Times New Roman", "SimSun", serif;
  font-size: 15px;
  font-weight: 400;
  color: var(--mc);
  margin: 0 0 10px;
}


.section-title::before,
.section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--mc), transparent);
}

.section-title-text {
  padding: 0 8px;
  letter-spacing: 1px;
}

/* --- Timeline --- */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.timeline-item {
  display: flex;
  gap: 12px;
}

.timeline-track {
  position: relative;
  width: 16px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.timeline-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--mc);
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px var(--mc);
  flex-shrink: 0;
  margin-top: 4px;
}

.timeline-line {
  width: 1px;
  flex: 1;
  background: linear-gradient(to bottom, var(--mc), transparent);
  margin-top: 4px;
}

.timeline-item:last-child .timeline-line {
  display: none;
}

.timeline-content {
  flex: 1;
}

/* --- Entry --- */
.entry-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 4px;
}

.entry-org {
  font-weight: 600;
  color: #222;
}

.entry-role {
  color: #555;
  font-size: 0.95em;
}

.entry-time {
  margin-left: auto;
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
}

.entry-detail {
  color: #555;
  word-break: break-word;
}

.entry-detail :deep(a) {
  color: var(--mc);
}
.entry-detail :deep(p) { margin: 2px 0; }
.entry-detail :deep(ul), .entry-detail :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.entry-detail :deep(li) { margin: 1px 0; }
.entry-detail :deep(li > p) { margin: 0; }

/* --- Skills --- */
.skill-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.skill-name {
  width: 100px;
  flex-shrink: 0;
  font-size: 13px;
  color: #555;
}

.skill-track {
  flex: 1;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.skill-fill {
  height: 100%;
  background: linear-gradient(to right, var(--mc), color-mix(in srgb, var(--mc) 60%, white));
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* --- Text content --- */
.text-content {
  color: #555;
  word-break: break-word;
}

.text-content :deep(a) {
  color: var(--mc);
}
.text-content :deep(p) { margin: 2px 0; }
.text-content :deep(ul), .text-content :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.text-content :deep(li) { margin: 1px 0; }
.text-content :deep(li > p) { margin: 0; }

/* --- Hobbies --- */
.hobby-list {
  color: #555;
  margin: 0;
}
</style>
