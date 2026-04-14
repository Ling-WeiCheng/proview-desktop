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
const cssMargin = computed(() => `${props.document.settings.marginMm}mm`)
</script>

<template>
  <div class="executive-page">
    <!-- Top decorative lines -->
    <div class="deco-lines">
      <div class="deco-line" style="width: 60%"></div>
      <div class="deco-line" style="width: 40%"></div>
      <div class="deco-line" style="width: 80%"></div>
    </div>

    <!-- Header block -->
    <div class="header-block">
      <div class="header-text">
        <h1 class="name">{{ document.basicInfo.name }}</h1>
        <p v-if="contactParts.length" class="contact-line">
          <span v-for="(part, i) in contactParts" :key="i">
            <span v-if="i > 0" class="sep"> | </span>{{ part }}
          </span>
        </p>
      </div>
      <img
        v-if="showPhoto"
        :src="document.basicInfo.photoUrl"
        class="photo"
        alt="照片"
      />
    </div>

    <!-- Modules -->
    <div class="body">
      <section v-for="mod in visibleModules" :key="mod.id" class="module">
        <!-- Intention -->
        <template v-if="mod.type === 'intention'">
          <div v-if="intentionLine(mod)" class="intention-bar">
            {{ intentionLine(mod) }}
          </div>
        </template>

        <!-- All other modules -->
        <template v-else>
          <h2 class="section-title"><span class="section-title-text">{{ mod.title }}</span></h2>

          <!-- Entry-based modules (timeline) -->
          <template v-if="isEntryType(mod.type) && mod.entries?.length">
            <div v-for="entry in mod.entries" :key="entry.id" class="timeline-entry">
              <div class="timeline-rail">
                <span class="timeline-dot"></span>
                <span class="timeline-line"></span>
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
          </template>

          <!-- Skills -->
          <template v-if="mod.type === 'skills'">
            <div v-if="mod.content" class="text-content" v-html="mod.content" />
          </template>

          <!-- Hobbies -->
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
  </div>
</template>

<style scoped>
/* --- Page --- */
.executive-page {
  --mc: v-bind(cssColor);
  --fs: v-bind(cssFontSize);
  --lh: v-bind(cssLineHeight);
  --mg: v-bind(cssMargin);
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

/* --- Decorative lines --- */
.deco-lines {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 18px var(--mg) 0;
}

.deco-line {
  height: 1px;
  background: var(--mc);
}

/* --- Header block --- */
.header-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--mc);
  margin: 12px var(--mg) 0;
  padding: 18px 24px;
  border-radius: 2px;
}

.header-text {
  flex: 1;
  min-width: 0;
}

.name {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
  letter-spacing: 2px;
}

.contact-line {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.88);
  margin: 0;
}

.sep {
  color: rgba(255, 255, 255, 0.5);
}

/* --- Photo --- */
.photo {
  width: 90px;
  height: 90px;
  object-fit: cover;
  flex-shrink: 0;
  margin-left: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
}

/* --- Body --- */
.body {
  padding: 0 var(--mg);
}

/* --- Intention bar --- */
.intention-bar {
  margin-top: 14px;
  padding: 8px 14px;
  border-left: 3px solid var(--mc);
  font-size: 13px;
  color: #444;
  background: #fafafa;
}

/* --- Module --- */
.module {
  margin-top: 18px;
}

/* --- Section title with diagonal cut --- */
.section-title {
  margin: 0 0 10px;
  padding: 0;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
}

.section-title-text {
  display: inline-block;
  padding: 5px 20px 5px 12px;
  background: var(--mc);
  color: #fff;
  letter-spacing: 1px;
  clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 100%, 0 100%);
}

/* --- Timeline entry --- */
.timeline-entry {
  display: flex;
  margin-bottom: 10px;
}

.timeline-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
  padding-top: 5px;
}

.timeline-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--mc);
  flex-shrink: 0;
}

.timeline-line {
  width: 2px;
  flex: 1;
  background: rgba(0, 0, 0, 0.08);
  margin-top: 2px;
}

.timeline-content {
  flex: 1;
  min-width: 0;
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
  font-size: 12px;
  color: #888;
}

.entry-detail {
  color: #555;
  line-height: var(--lh);
  word-break: break-word;
  font-size: var(--fs);
}

.entry-detail :deep(a) {
  color: var(--mc);
  text-decoration: none;
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
  background: var(--mc);
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
  color: var(--mc);
  border: 1px solid var(--mc);
  border-radius: 999px;
  line-height: 1.6;
}

/* --- Text content --- */
.text-content {
  color: #555;
  line-height: var(--lh);
  word-break: break-word;
}

.text-content :deep(a) {
  color: var(--mc);
  text-decoration: none;
}
.text-content :deep(p) { margin: 2px 0; }
.text-content :deep(ul), .text-content :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.text-content :deep(li) { margin: 1px 0; }
.text-content :deep(li > p) { margin: 0; }
</style>
