<script setup lang="ts">
import { computed } from 'vue'
import type { ResumeDocument, ResumeModule, ModuleType } from '../../types/resume-builder'

const props = defineProps<{ document: ResumeDocument }>()

const visibleModules = computed(() =>
  [...props.document.modules].filter(m => m.visible).sort((a, b) => a.sortIndex - b.sortIndex),
)

const contactParts = computed(() => {
  const b = props.document.basicInfo
  return [b.mobile, b.email, b.location].filter(Boolean)
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

const bannerIntention = computed(() => {
  const mod = props.document.modules.find(m => m.type === 'intention' && m.visible)
  return mod ? intentionLine(mod) : ''
})
</script>

<template>
  <div class="fresh-page">
    <!-- Top Banner -->
    <div class="banner">
      <div class="banner-left">
        <h1 class="banner-name">{{ document.basicInfo.name }}</h1>
        <p v-if="bannerIntention" class="banner-intention">
          {{ bannerIntention }}
        </p>
      </div>
      <img
        v-if="showPhoto"
        :src="document.basicInfo.photoUrl"
        class="banner-photo"
        alt="照片"
      />
    </div>

    <!-- Contact Row -->
    <div v-if="contactParts.length" class="contact-row">
      <span v-for="(part, i) in contactParts" :key="i">
        <span v-if="i > 0" class="contact-dot">●</span>{{ part }}
      </span>
    </div>

    <!-- Modules -->
    <section v-for="mod in visibleModules" :key="mod.id" class="module">
      <!-- Skip intention (already in banner) -->
      <template v-if="mod.type === 'intention'" />

      <!-- All other modules -->
      <template v-else>
        <div class="section-header">
          <span class="section-bar" />
          <span class="section-tag">{{ mod.title }}</span>
        </div>

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
</template>

<style scoped>
/* --- Page --- */
.fresh-page {
  --mc: v-bind(cssColor);
  --fs: v-bind(cssFontSize);
  --lh: v-bind(cssLineHeight);
  --mg: v-bind(cssMargin);
  position: relative;
  width: 794px;
  min-height: 1123px;
  background: #fff;
  color: #333;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: var(--fs);
  line-height: var(--lh);
  box-sizing: border-box;
  overflow: hidden;
}

/* --- Banner --- */
.banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--mc);
  color: #fff;
  padding: 22px 28px;
  min-height: 80px;
}

.banner-left {
  flex: 1;
  min-width: 0;
}

.banner-name {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 3px;
  margin: 0 0 4px;
}

.banner-intention {
  font-size: 13px;
  margin: 0;
  opacity: 0.9;
}

.banner-photo {
  width: 90px;
  height: 115px;
  object-fit: cover;
  border-radius: 6px;
  border: 3px solid #fff;
  margin-left: 20px;
  flex-shrink: 0;
}

/* --- Contact Row --- */
.contact-row {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 12.5px;
  color: #555;
  padding: 10px 28px;
  border-bottom: 1px solid #eee;
}

.contact-dot {
  margin: 0 8px;
  font-size: 6px;
  color: var(--mc);
  vertical-align: middle;
}

/* --- Section Header --- */
.module {
  padding: 0 var(--mg);
  margin-top: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.section-bar {
  width: 3px;
  height: 18px;
  background: var(--mc);
  border-radius: 2px;
  flex-shrink: 0;
}

.section-tag {
  display: inline-block;
  background: var(--mc);
  color: #fff;
  font-size: 13.5px;
  font-weight: 600;
  padding: 2px 12px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

/* --- Entry --- */
.entry {
  margin-bottom: 10px;
  padding-left: 14px;
  position: relative;
}

.entry::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--mc);
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
  background: color-mix(in srgb, var(--mc) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--mc) 30%, transparent);
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
