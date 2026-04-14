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

const leftTypes: ModuleType[] = ['education', 'skills', 'certificates', 'hobbies']
const rightTypes: ModuleType[] = ['work', 'project', 'internship', 'campus', 'evaluation', 'custom']

const leftModules = computed(() =>
  visibleModules.value.filter(m => leftTypes.includes(m.type) && m.type !== 'intention'),
)

const rightModules = computed(() =>
  visibleModules.value.filter(m => rightTypes.includes(m.type) && m.type !== 'intention'),
)

const intentionModule = computed(() =>
  visibleModules.value.find(m => m.type === 'intention'),
)

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
  <div class="compact-page">
    <!-- Header -->
    <header class="compact-header">
      <div class="header-left">
        <h1 class="name">{{ document.basicInfo.name }}</h1>
      </div>
      <div class="header-right">
        <p v-if="contactParts.length" class="contact-info">
          <span v-for="(part, i) in contactParts" :key="i">
            <span v-if="i > 0" class="pipe"> | </span>{{ part }}
          </span>
        </p>
      </div>
      <img
        v-if="showPhoto"
        :src="document.basicInfo.photoUrl"
        class="photo"
        alt="照片"
      />
    </header>

    <!-- Intention line -->
    <p
      v-if="intentionModule && intentionLine(intentionModule)"
      class="intention-line"
    >
      {{ intentionLine(intentionModule) }}
    </p>

    <!-- Two-column content -->
    <div class="columns">
      <!-- Left column (48%) -->
      <div class="col-left">
        <section v-for="mod in leftModules" :key="mod.id" class="module">
          <h2 class="section-title">{{ mod.title }}</h2>

          <!-- Entry-based -->
          <template v-if="isEntryType(mod.type) && mod.entries?.length">
            <div v-for="entry in mod.entries" :key="entry.id" class="entry">
              <div class="entry-head">
                <span class="entry-org">{{ entry.orgName }}</span>
                <span v-if="entry.role" class="entry-role"> · {{ entry.role }}</span>
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

          <!-- Certificates -->
          <template v-if="mod.type === 'certificates'">
            <div v-if="mod.content" class="text-content" v-html="mod.content" />
          </template>

          <!-- Hobbies -->
          <template v-if="mod.type === 'hobbies'">
            <p v-if="mod.tags?.length" class="hobby-text">{{ mod.tags.join('，') }}</p>
            <div v-else-if="mod.content" class="text-content" v-html="mod.content" />
          </template>
        </section>
      </div>

      <!-- Right column (52%) -->
      <div class="col-right">
        <section v-for="mod in rightModules" :key="mod.id" class="module">
          <h2 class="section-title">{{ mod.title }}</h2>

          <!-- Entry-based -->
          <template v-if="isEntryType(mod.type) && mod.entries?.length">
            <div v-for="entry in mod.entries" :key="entry.id" class="entry">
              <div class="entry-head">
                <span class="entry-org">{{ entry.orgName }}</span>
                <span v-if="entry.role" class="entry-role"> · {{ entry.role }}</span>
                <span class="entry-time">
                  {{ formatTimeRange(entry.timeStart, entry.timeEnd, entry.isCurrent) }}
                </span>
              </div>
              <div v-if="entry.detail" class="entry-detail" v-html="entry.detail" />
            </div>
          </template>

          <!-- Text-only: evaluation, custom -->
          <template v-if="['evaluation', 'custom'].includes(mod.type)">
            <div v-if="mod.content" class="text-content" v-html="mod.content" />
          </template>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- Page --- */
.compact-page {
  --mc: v-bind(cssColor);
  --fs: v-bind(cssFontSize);
  --lh: v-bind(cssLineHeight);
  width: 794px;
  min-height: 1123px;
  background: #fff;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: var(--fs);
  line-height: var(--lh);
  color: #333;
  box-sizing: border-box;
  overflow: hidden;
  padding: 20px;
}

/* --- Header --- */
.compact-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.header-left {
  flex-shrink: 0;
}

.name {
  font-size: 20px;
  font-weight: 700;
  color: var(--mc);
  margin: 0;
  letter-spacing: 1px;
}

.header-right {
  flex: 1;
  text-align: right;
}

.contact-info {
  font-size: 11px;
  color: #666;
  margin: 0;
}

.pipe {
  color: #ccc;
}

/* --- Photo --- */
.photo {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

/* --- Intention --- */
.intention-line {
  font-size: 12px;
  color: #555;
  margin: 0 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e0e0e0;
}

/* --- Two-column layout --- */
.columns {
  display: flex;
  gap: 16px;
}

.col-left {
  width: 48%;
  flex-shrink: 0;
}

.col-right {
  width: 52%;
  flex-shrink: 0;
}

/* --- Module --- */
.module {
  margin-bottom: 10px;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--mc);
  margin: 0 0 4px;
  padding-bottom: 2px;
  border-bottom: 1px solid var(--mc);
}

/* --- Entry --- */
.entry {
  margin-bottom: 6px;
}

.entry-head {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 2px;
  font-size: 11px;
}

.entry-org {
  font-weight: 600;
  color: #222;
}

.entry-role {
  color: #555;
}

.entry-time {
  margin-left: auto;
  font-size: 10px;
  color: #999;
  flex-shrink: 0;
}

.entry-detail {
  font-size: 11px;
  color: #555;
  word-break: break-word;
  line-height: 1.4;
}

.entry-detail :deep(a) {
  color: var(--mc);
}
.entry-detail :deep(p) { margin: 2px 0; }
.entry-detail :deep(ul), .entry-detail :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.entry-detail :deep(li) { margin: 1px 0; }
.entry-detail :deep(li > p) { margin: 0; }

/* --- Text content --- */
.text-content {
  font-size: 11px;
  color: #555;
  word-break: break-word;
  line-height: 1.4;
}

.text-content :deep(a) {
  color: var(--mc);
}
.text-content :deep(p) { margin: 2px 0; }
.text-content :deep(ul), .text-content :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.text-content :deep(li) { margin: 1px 0; }
.text-content :deep(li > p) { margin: 0; }

/* --- Skills inline --- */
.skill-inline {
  font-size: 11px;
  color: #555;
  margin: 0;
  line-height: 1.5;
}

/* --- Hobbies --- */
.hobby-text {
  font-size: 11px;
  color: #555;
  margin: 0;
  line-height: 1.5;
}
</style>
