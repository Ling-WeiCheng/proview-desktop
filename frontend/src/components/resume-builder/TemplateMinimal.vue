<script setup lang="ts">
import { computed } from 'vue'
import type { ResumeDocument, ModuleType } from '../../types/resume-builder'

const props = defineProps<{ document: ResumeDocument }>()

const visibleModules = computed(() =>
  [...props.document.modules].filter(m => m.visible).sort((a, b) => a.sortIndex - b.sortIndex)
)

const entryTypes: ModuleType[] = ['education', 'work', 'project', 'internship', 'campus']

const contactParts = computed(() => {
  const b = props.document.basicInfo
  return [b.mobile, b.email, b.location].filter(Boolean)
})

function formatTime(start: string, end: string, cur: boolean) {
  if (!start && !end) return ''
  return `${start} - ${cur ? '至今' : end}`
}

function intentionLine(mod: any) {
  if (!mod.intention) return ''
  const { targetJob, targetCity, salary } = mod.intention
  return [targetJob, targetCity, salary].filter(Boolean).join(' / ')
}

const showPhoto = computed(
  () => props.document.settings.photoShow && !!props.document.basicInfo.photoUrl,
)

const cssColor = computed(() => props.document.settings.themeColor)
const cssFontSize = computed(() => `${props.document.settings.fontSize}px`)
const cssLineHeight = computed(() => String(props.document.settings.lineHeight))
const cssMargin = computed(() => `${props.document.settings.marginMm}mm`)

const intentionModule = computed(() =>
  props.document.modules.find(m => m.type === 'intention' && m.visible && intentionLine(m))
)
</script>

<template>
  <div class="minimal-page">
    <!-- Header -->
    <header class="header">
      <div class="header-main">
        <h1 class="name">{{ document.basicInfo.name }}</h1>
        <p v-if="contactParts.length" class="contact">
          {{ contactParts.join('  ·  ') }}
        </p>
        <p v-if="intentionModule" class="intention-inline">
          {{ intentionLine(intentionModule) }}
        </p>
      </div>
      <img v-if="showPhoto" :src="document.basicInfo.photoUrl" class="photo" alt="照片" />
    </header>

    <!-- Modules -->
    <template v-for="mod in visibleModules" :key="mod.id">
      <!-- Intention already shown in header, skip -->
      <section v-if="mod.type !== 'intention'" class="section">
        <h2 class="section-title">{{ mod.title }}</h2>
        <div class="divider" />

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

        <template v-if="mod.type === 'skills'">
          <div v-if="mod.content" class="text-block" v-html="mod.content" />
        </template>

        <template v-if="mod.type === 'hobbies'">
          <div v-if="mod.tags?.length" class="skill-list">
            <span v-for="(t, i) in mod.tags" :key="i" class="skill-chip">{{ t }}</span>
          </div>
          <div v-else-if="mod.content" class="text-block" v-html="mod.content" />
        </template>

        <template v-if="['certificates', 'evaluation', 'custom'].includes(mod.type)">
          <div v-if="mod.content" class="text-block" v-html="mod.content" />
        </template>
      </section>
    </template>
  </div>
</template>

<style scoped>
.minimal-page {
  --mc: v-bind(cssColor);
  --fs: v-bind(cssFontSize);
  --lh: v-bind(cssLineHeight);
  --mg: v-bind(cssMargin);
  width: 794px;
  min-height: 1123px;
  background: #fff;
  color: #444;
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: var(--fs);
  line-height: var(--lh);
  padding: 30px var(--mg);
  box-sizing: border-box;
  overflow: hidden;
}

.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.header-main { flex: 1; }
.photo { width: 90px; height: 120px; object-fit: cover; border-radius: 4px; flex-shrink: 0; margin-left: 16px; }
.name { font-size: 22px; font-weight: 700; margin: 0 0 4px; color: var(--mc); letter-spacing: 1px; }
.contact { font-size: 12px; color: #888; margin: 0; }
.intention-inline { font-size: 12px; color: #666; margin: 4px 0 0; }

.intention { font-size: 12.5px; color: #666; margin-bottom: 8px; }

.section { margin-top: 16px; }
.section-title { font-size: 14px; font-weight: 600; color: #333; margin: 0 0 3px; text-transform: uppercase; letter-spacing: 0.5px; }
.divider { height: 1px; background: #e0e0e0; margin-bottom: 8px; }

.entry { margin-bottom: 10px; }
.entry-head { display: flex; align-items: baseline; gap: 6px; margin-bottom: 2px; }
.entry-org { font-weight: 600; color: #333; }
.entry-role { color: #666; }
.entry-time { margin-left: auto; font-size: 12px; color: #aaa; flex-shrink: 0; }
.entry-detail { color: #555; word-break: break-word; }
.entry-detail :deep(a) { color: var(--mc); }
.entry-detail :deep(p) { margin: 2px 0; }
.entry-detail :deep(ul), .entry-detail :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.entry-detail :deep(li) { margin: 1px 0; }
.entry-detail :deep(li > p) { margin: 0; }

.text-block { color: #555; word-break: break-word; }
.text-block :deep(a) { color: var(--mc); }
.text-block :deep(p) { margin: 2px 0; }
.text-block :deep(ul), .text-block :deep(ol) { margin: 2px 0 2px 16px; padding: 0; }
.text-block :deep(li) { margin: 1px 0; }
.text-block :deep(li > p) { margin: 0; }

.skill-list { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.skill-chip { font-size: 12px; padding: 2px 12px; background: #f5f5f5; border-radius: 4px; color: #555; }
</style>
