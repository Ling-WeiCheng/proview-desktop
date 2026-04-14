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

const entryTypes: ModuleType[] = ['education', 'work', 'project', 'internship', 'campus']

const showPhoto = computed(
  () => props.document.settings.photoShow && !!props.document.basicInfo.photoUrl,
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
const cssMargin = computed(() => `${props.document.settings.marginMm}mm`)
</script>

<template>
  <div class="tech-page">
    <!-- Dark Header Bar -->
    <header class="tech-header">
      <div class="tech-header-main">
        <h1 class="tech-name">{{ document.basicInfo.name }}</h1>
        <p v-if="document.basicInfo.workYears" class="tech-subtitle">
          {{ document.basicInfo.workYears }} 经验
        </p>
        <p v-if="contactParts.length" class="tech-contact">
          <span v-for="(part, i) in contactParts" :key="i">
            <span v-if="i > 0" class="pipe"> | </span>{{ part }}
          </span>
        </p>
      </div>
      <img v-if="showPhoto" :src="document.basicInfo.photoUrl" class="tech-photo" alt="照片" />
    </header>

    <!-- Modules -->
    <section v-for="mod in visibleModules" :key="mod.id" class="tech-module">
      <!-- Intention -->
      <template v-if="mod.type === 'intention'">
        <p v-if="intentionLine(mod)" class="tech-intention">
          {{ intentionLine(mod) }}
        </p>
      </template>

      <!-- All other modules -->
      <template v-else>
        <h2 class="tech-section-title">// {{ mod.title }}</h2>

        <!-- Entry-based modules -->
        <template v-if="isEntryType(mod.type) && mod.entries?.length">
          <div v-for="entry in mod.entries" :key="entry.id" class="tech-entry">
            <div class="tech-entry-head">
              <span class="tech-entry-org">{{ entry.orgName }}</span>
              <span v-if="entry.role"> — {{ entry.role }}</span>
              <span class="tech-entry-time">
                {{ formatTimeRange(entry.timeStart, entry.timeEnd, entry.isCurrent) }}
              </span>
            </div>
            <div v-if="entry.detail" class="tech-entry-detail" v-html="entry.detail" />
          </div>
        </template>

        <!-- Skills -->
        <template v-if="mod.type === 'skills'">
          <div v-if="mod.content" class="tech-text" v-html="mod.content" />
        </template>

        <!-- Hobbies -->
        <template v-if="mod.type === 'hobbies'">
          <div v-if="mod.tags?.length" class="tech-tags">
            <span v-for="(tag, i) in mod.tags" :key="i" class="tech-pill">{{ tag }}</span>
          </div>
          <div v-else-if="mod.content" class="tech-text" v-html="mod.content" />
        </template>

        <!-- Text-only: certificates / evaluation / custom -->
        <template v-if="['certificates', 'evaluation', 'custom'].includes(mod.type)">
          <div v-if="mod.content" class="tech-text" v-html="mod.content" />
        </template>
      </template>
    </section>
  </div>
</template>

<style scoped>
/* --- Page --- */
.tech-page {
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
  padding: 0 0 25px;
  box-sizing: border-box;
  overflow: hidden;
}

/* --- Dark Header --- */
.tech-header {
  background: #1a1a2e;
  padding: 28px var(--mg) 22px;
  margin-bottom: 4px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.tech-header-main { flex: 1; }

.tech-photo {
  width: 90px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
  margin-left: 20px;
  border: 2px solid rgba(255,255,255,0.15);
}

.tech-name {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 4px;
  letter-spacing: 3px;
}

.tech-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 10px;
}

.tech-contact {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.pipe {
  margin: 0 6px;
  color: rgba(255, 255, 255, 0.35);
}
/* --- Intention --- */
.tech-intention {
  font-size: 13px;
  color: var(--mc);
  margin: 0;
  padding: 6px var(--mg);
}

/* --- Module --- */
.tech-module {
  margin-top: 16px;
  padding: 0 var(--mg);
}

/* --- Section Title (code-comment style) --- */
.tech-section-title {
  font-family: Consolas, "Courier New", monospace;
  font-size: 15px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px;
  padding-bottom: 5px;
  border-bottom: 1.5px dashed var(--mc);
  letter-spacing: 0.5px;
}

/* --- Entry --- */
.tech-entry {
  margin-bottom: 12px;
}

.tech-entry-head {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 4px;
  font-size: var(--fs);
  color: #444;
}

.tech-entry-org {
  font-weight: 700;
  color: #222;
}

.tech-entry-time {
  margin-left: auto;
  flex-shrink: 0;
  font-family: Consolas, "Courier New", monospace;
  font-size: 12px;
  color: #888;
}

.tech-entry-detail {
  background: #f8f9fa;
  border-left: 3px solid var(--mc);
  padding: 8px 12px;
  color: #555;
  line-height: var(--lh);
  word-break: break-word;
  font-size: var(--fs);
  border-radius: 0 4px 4px 0;
}

.tech-entry-detail :deep(a) {
  color: var(--mc);
  text-decoration: none;
}
.tech-entry-detail :deep(p) { margin: 2px 0; }
.tech-entry-detail :deep(ul), .tech-entry-detail :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.tech-entry-detail :deep(li) { margin: 1px 0; }
.tech-entry-detail :deep(li > p) { margin: 0; }
/* --- Skill / Hobby Tags (pill cloud) --- */
.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.tech-pill {
  display: inline-block;
  padding: 3px 14px;
  font-size: 12px;
  color: #fff;
  background: var(--mc);
  border-radius: 999px;
  line-height: 1.6;
}

/* --- Text content --- */
.tech-text {
  color: #555;
  line-height: var(--lh);
  word-break: break-word;
}

.tech-text :deep(a) {
  color: var(--mc);
  text-decoration: none;
}
.tech-text :deep(p) { margin: 2px 0; }
.tech-text :deep(ul), .tech-text :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.tech-text :deep(li) { margin: 1px 0; }
.tech-text :deep(li > p) { margin: 0; }
</style>
