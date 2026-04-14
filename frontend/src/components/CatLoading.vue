<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  message?: string
  thinkingText?: string
  stage?: string
  blocking?: boolean
  variant?: 'fullscreen' | 'corner'
}>(), {
  blocking: false,
  variant: 'fullscreen',
})

const catEl = ref<HTMLElement | null>(null)
const thinkingBox = ref<HTMLElement | null>(null)
const expandedThinkingBox = ref<HTMLElement | null>(null)
const isExpanded = ref(false)
const isCorner = computed(() => props.variant === 'corner')
const canExpandThinking = computed(() => (
  isCorner.value
  && Boolean(props.thinkingText?.trim())
))

const rainColumns = Array.from({ length: 22 }, (_, idx) => ({
  id: idx,
  left: `${((idx + 0.5) / 22) * 100}%`,
  delay: `-${(idx % 7) * 0.55}s`,
  duration: `${5.2 + (idx % 6) * 0.9}s`,
}))
const rainGlyphs = '0100110101101001110010110100100110100101101001'

const CAT_MAP = [
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,1,1,2,1,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,0,1,2,2,1,1,1,1,1,2,2,1,0,0],
  [0,0,0,0,0,0,0,0,0,0,0,1,2,2,1,1,1,1,1,1,1,2,1,0,0],
  [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,2,2,2,1,1,1,2,2,2,1],
  [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
  [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
]

onMounted(() => {
  if (!catEl.value) return
  const px = 4
  const shadows: string[] = []
  CAT_MAP.forEach((row, y) => {
    row.forEach((t, x) => {
      const c = t === 1 ? '#10201b' : t === 2 ? '#d9ffe7' : ''
      if (c) shadows.push(`${x * px}px ${y * px}px 0 ${c}`)
    })
  })
  catEl.value.style.boxShadow = shadows.join(',')
})

watch(() => props.thinkingText, () => {
  nextTick(() => {
    if (thinkingBox.value) {
      thinkingBox.value.scrollTop = thinkingBox.value.scrollHeight
    }
    if (expandedThinkingBox.value) {
      expandedThinkingBox.value.scrollTop = expandedThinkingBox.value.scrollHeight
    }
  })
})

watch(canExpandThinking, (enabled) => {
  if (!enabled) {
    isExpanded.value = false
  }
})

function openExpandedPreview() {
  if (!canExpandThinking.value) return
  isExpanded.value = true
}

function closeExpandedPreview() {
  isExpanded.value = false
}

function handleWindowKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && isExpanded.value) {
    closeExpandedPreview()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleWindowKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleWindowKeydown)
})
</script>

<script lang="ts">
export default {
  name: 'CatLoading',
}
</script>

<template>
  <Teleport to="body">
    <Transition name="cat-fade">
      <div
        class="cat-shell"
        :class="{
          'cat-shell--corner': isCorner,
          'cat-shell--passthrough': !props.blocking,
        }"
      >
        <div class="cat-shell__inner" :class="{ 'cat-shell__inner--corner': isCorner }">
          <section class="matrix-panel" :class="{ 'matrix-panel--corner': isCorner }">
            <div class="matrix-rain" aria-hidden="true">
              <span
                v-for="col in rainColumns"
                :key="col.id"
                class="rain-col"
                :style="{
                  left: col.left,
                  animationDelay: col.delay,
                  animationDuration: col.duration,
                }"
              >
                {{ rainGlyphs }}
              </span>
            </div>

            <div class="scanline" aria-hidden="true"></div>

            <div class="console-body">
              <div class="console-head">
                <span class="dot dot--red"></span>
                <span class="dot dot--yellow"></span>
                <span class="dot dot--green"></span>
                <span class="head-title">MATRIX CORE</span>
              </div>

              <div class="display-wrap">
                <div class="display-frame">
                  <div class="display-grid"></div>
                  <div ref="catEl" class="pixel-cat"></div>
                  <div class="loading-ui">
                    <div class="loading-label">SYSTEM SYNCING</div>
                    <div class="pixel-bar"><div class="bar-fill"></div></div>
                    <div class="loading-sub">linking neural interview pipeline...</div>
                  </div>
                </div>
              </div>

              <div class="console-foot">
                <div class="chip-line"></div>
                <div class="chip-line"></div>
                <div class="chip-line"></div>
              </div>
            </div>
          </section>

          <div class="status-card" :class="{ 'status-card--corner': isCorner }">
            <button
              v-if="canExpandThinking"
              type="button"
              class="status-expand-trigger"
              @click="isExpanded ? closeExpandedPreview() : openExpandedPreview()"
            >
              {{ isExpanded ? '收起窗口' : '放大查看' }}
            </button>
            <p class="status-text">{{ message || 'AI 面试官正在接入矩阵通道...' }}</p>
            <p v-if="stage" class="stage-text">{{ stage }}</p>
            <div
              v-if="thinkingText"
              ref="thinkingBox"
              class="thinking-box"
              :class="{
                'thinking-box--corner': isCorner,
                'thinking-box--expandable': canExpandThinking,
              }"
              :role="canExpandThinking ? 'button' : undefined"
              :tabindex="canExpandThinking ? 0 : undefined"
              @click="canExpandThinking && openExpandedPreview()"
              @keydown.enter.prevent="canExpandThinking && openExpandedPreview()"
              @keydown.space.prevent="canExpandThinking && openExpandedPreview()"
            >
              <div class="thinking-content">{{ thinkingText }}</div>
            </div>
          </div>

          <section
            v-if="isExpanded"
            class="expanded-preview-panel"
          >
            <div class="expanded-preview-header">
              <div>
                <p class="expanded-preview-kicker">LIVE PREVIEW</p>
                <h3 class="expanded-preview-title">{{ message || 'AI 面试官正在处理当前任务' }}</h3>
                <p v-if="stage" class="expanded-preview-stage">{{ stage }}</p>
              </div>
              <button
                type="button"
                class="expanded-preview-close"
                @click="closeExpandedPreview"
              >
                关闭
              </button>
            </div>

            <div
              ref="expandedThinkingBox"
              class="expanded-thinking-box custom-scroll"
            >
              <div class="thinking-content">{{ thinkingText }}</div>
            </div>
          </section>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.cat-fade-enter-active, .cat-fade-leave-active { transition: opacity .35s ease; }
.cat-fade-enter-from, .cat-fade-leave-to { opacity: 0; }

.cat-shell {
  --cat-shell-overlay: rgba(241, 245, 249, 0.78);
  --cat-shell-halo-a: rgba(59, 130, 246, 0.16);
  --cat-shell-halo-b: rgba(20, 184, 166, 0.14);
  --cat-panel-border: rgba(59, 130, 246, 0.18);
  --cat-panel-start: rgba(255, 255, 255, 0.95);
  --cat-panel-end: rgba(226, 232, 240, 0.92);
  --cat-panel-inset: rgba(59, 130, 246, 0.1);
  --cat-panel-shadow: 0 28px 70px rgba(59, 130, 246, 0.16);
  --cat-panel-glow: 0 0 48px rgba(20, 184, 166, 0.1);
  --cat-rain: rgba(37, 99, 235, 0.48);
  --cat-rain-glow: rgba(37, 99, 235, 0.26);
  --cat-scanline: rgba(56, 189, 248, 0.12);
  --cat-head-text: rgba(30, 64, 175, 0.82);
  --cat-display-border: rgba(56, 189, 248, 0.24);
  --cat-display-start: rgba(255, 255, 255, 0.96);
  --cat-display-end: rgba(224, 242, 254, 0.92);
  --cat-grid: rgba(56, 189, 248, 0.08);
  --cat-pixel-shadow: rgba(56, 189, 248, 0.24);
  --cat-chip: rgba(59, 130, 246, 0.24);
  --cat-bar-border: rgba(59, 130, 246, 0.28);
  --cat-bar-bg: rgba(219, 234, 254, 0.82);
  --cat-bar-start: #38bdf8;
  --cat-bar-end: #34d399;
  --cat-loading-label: rgba(30, 64, 175, 0.9);
  --cat-loading-sub: rgba(8, 145, 178, 0.78);
  --cat-status-border: rgba(59, 130, 246, 0.18);
  --cat-status-start: rgba(255, 255, 255, 0.96);
  --cat-status-end: rgba(226, 232, 240, 0.92);
  --cat-status-shadow: 0 14px 40px rgba(59, 130, 246, 0.14);
  --cat-status-text: rgba(15, 23, 42, 0.84);
  --cat-stage-text: rgba(8, 145, 178, 0.88);
  --cat-thinking-border: rgba(56, 189, 248, 0.18);
  --cat-thinking-bg: rgba(255, 255, 255, 0.76);
  --cat-thinking-scrollbar: rgba(56, 189, 248, 0.32);
  --cat-thinking-text: rgba(15, 23, 42, 0.76);
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 15% 15%, var(--cat-shell-halo-a), transparent 40%),
    radial-gradient(circle at 85% 80%, var(--cat-shell-halo-b), transparent 45%),
    var(--cat-shell-overlay);
  backdrop-filter: blur(10px);
}

.cat-shell--corner {
  inset: 1rem 1rem auto auto;
  z-index: 60;
  display: flex;
  justify-content: flex-end;
  background: transparent;
  backdrop-filter: none;
}

.cat-shell--passthrough {
  pointer-events: none;
}

:global(html.dark) .cat-shell {
  --cat-shell-overlay: rgba(1, 10, 8, 0.78);
  --cat-shell-halo-a: rgba(56, 189, 120, 0.18);
  --cat-shell-halo-b: rgba(16, 185, 129, 0.14);
  --cat-panel-border: rgba(110, 231, 183, 0.22);
  --cat-panel-start: rgba(2, 26, 21, 0.95);
  --cat-panel-end: rgba(1, 9, 7, 0.92);
  --cat-panel-inset: rgba(16, 185, 129, 0.08);
  --cat-panel-shadow: 0 28px 70px rgba(0, 0, 0, 0.45);
  --cat-panel-glow: 0 0 52px rgba(16, 185, 129, 0.14);
  --cat-rain: rgba(110, 231, 183, 0.6);
  --cat-rain-glow: rgba(110, 231, 183, 0.7);
  --cat-scanline: rgba(16, 185, 129, 0.15);
  --cat-head-text: rgba(167, 243, 208, 0.9);
  --cat-display-border: rgba(110, 231, 183, 0.3);
  --cat-display-start: rgba(4, 33, 27, 0.96);
  --cat-display-end: rgba(5, 21, 18, 0.93);
  --cat-grid: rgba(110, 231, 183, 0.08);
  --cat-pixel-shadow: rgba(110, 231, 183, 0.5);
  --cat-chip: rgba(167, 243, 208, 0.6);
  --cat-bar-border: rgba(110, 231, 183, 0.36);
  --cat-bar-bg: rgba(4, 34, 27, 0.92);
  --cat-bar-start: #34d399;
  --cat-bar-end: #6ee7b7;
  --cat-loading-label: rgba(209, 250, 229, 0.92);
  --cat-loading-sub: rgba(134, 239, 172, 0.74);
  --cat-status-border: rgba(110, 231, 183, 0.24);
  --cat-status-start: rgba(5, 26, 21, 0.95);
  --cat-status-end: rgba(3, 14, 12, 0.9);
  --cat-status-shadow: 0 14px 40px rgba(0, 0, 0, 0.38);
  --cat-status-text: rgba(209, 250, 229, 0.88);
  --cat-stage-text: rgba(110, 231, 183, 0.92);
  --cat-thinking-border: rgba(110, 231, 183, 0.22);
  --cat-thinking-bg: rgba(2, 18, 15, 0.55);
  --cat-thinking-scrollbar: rgba(110, 231, 183, 0.35);
  --cat-thinking-text: rgba(167, 243, 208, 0.9);
}

:global(html.dark) .cat-shell--corner { background: transparent; }

.cat-shell__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
  pointer-events: auto;
}

.cat-shell__inner--corner {
  flex-direction: column;
  align-items: flex-end;
}

.matrix-panel {
  position: relative;
  width: min(38rem, 92vw);
  border-radius: 1.2rem;
  border: 1px solid var(--cat-panel-border);
  background:
    linear-gradient(150deg, var(--cat-panel-start), var(--cat-panel-end));
  box-shadow:
    0 0 0 1px var(--cat-panel-inset) inset,
    var(--cat-panel-shadow),
    var(--cat-panel-glow);
  overflow: hidden;
}

.matrix-panel--corner {
  width: clamp(16rem, 30vw, 20rem);
}

.matrix-rain {
  position: absolute;
  inset: 0;
  overflow: hidden;
  opacity: 0.35;
  pointer-events: none;
}

.rain-col {
  position: absolute;
  top: -6rem;
  color: var(--cat-rain);
  font-family: 'Cascadia Mono', 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 0.66rem;
  line-height: 1.15;
  letter-spacing: 0.08em;
  white-space: pre-wrap;
  animation-name: rain-fall;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  text-shadow: 0 0 8px var(--cat-rain-glow);
}

@keyframes rain-fall {
  0% { transform: translateY(-32%); opacity: 0; }
  10% { opacity: 0.75; }
  95% { opacity: 0.6; }
  100% { transform: translateY(130%); opacity: 0; }
}

.scanline {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent, var(--cat-scanline), transparent);
  mix-blend-mode: screen;
  animation: scanline-move 3.6s linear infinite;
  pointer-events: none;
}

@keyframes scanline-move {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(120%); }
}

.console-body {
  position: relative;
  z-index: 2;
  padding: 0.9rem 0.9rem 0.75rem;
}

.console-head {
  display: flex;
  align-items: center;
  gap: 0.38rem;
}

.dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 999px;
}

.dot--red { background: #fb7185; }
.dot--yellow { background: #fbbf24; }
.dot--green { background: #4ade80; }

.head-title {
  margin-left: auto;
  color: var(--cat-head-text);
  font-size: 0.66rem;
  letter-spacing: 0.14em;
  font-weight: 700;
  text-transform: uppercase;
}

.display-wrap {
  margin-top: 0.7rem;
}

.display-frame {
  --px: 4px;
  position: relative;
  border-radius: 0.9rem;
  border: 1px solid var(--cat-display-border);
  background: linear-gradient(140deg, var(--cat-display-start), var(--cat-display-end));
  min-height: 11.8rem;
  overflow: hidden;
}

.matrix-panel--corner .display-frame {
  min-height: 9.2rem;
}

.display-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(90deg, var(--cat-grid) 1px, transparent 1px),
    linear-gradient(var(--cat-grid) 1px, transparent 1px);
  background-size: 10px 10px;
}

.pixel-cat {
  position: absolute;
  top: 42%;
  left: 50%;
  width: 4px;
  height: 4px;
  image-rendering: pixelated;
  margin-left: -52px;
  margin-top: -32px;
  filter: drop-shadow(0 0 9px var(--cat-pixel-shadow));
}

.pixel-cat::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 4px;
  animation: tail-wag .6s steps(2) infinite;
}

@keyframes tail-wag {
  0% {
    box-shadow:
      4px 40px 0 #10201b, 8px 40px 0 #10201b, 12px 40px 0 #10201b, 16px 40px 0 #10201b,
      0px 44px 0 #10201b, 4px 44px 0 #10201b, 8px 44px 0 #10201b, 12px 44px 0 #10201b, 16px 44px 0 #10201b, 20px 44px 0 #10201b,
      0px 48px 0 #10201b, 4px 48px 0 #10201b, 8px 48px 0 #10201b;
  }
  100% {
    box-shadow:
      4px 36px 0 #10201b, 8px 36px 0 #10201b, 12px 36px 0 #10201b, 16px 36px 0 #10201b,
      0px 40px 0 #10201b, 4px 40px 0 #10201b, 8px 40px 0 #10201b, 12px 40px 0 #10201b, 16px 40px 0 #10201b, 20px 40px 0 #10201b,
      0px 44px 0 #10201b, 4px 44px 0 #10201b, 8px 44px 0 #10201b;
  }
}

.console-foot {
  margin-top: 0.65rem;
  display: flex;
  gap: 0.45rem;
}

.chip-line {
  flex: 1;
  height: 0.25rem;
  border-radius: 999px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--cat-chip) 20%, transparent), var(--cat-chip), color-mix(in srgb, var(--cat-chip) 20%, transparent));
}

.loading-ui {
  position: absolute;
  left: 0.8rem;
  right: 0.8rem;
  bottom: 0.72rem;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.28rem;
}

.pixel-bar {
  width: 100%;
  height: 0.46rem;
  border-radius: 999px;
  border: 1px solid var(--cat-bar-border);
  padding: 0.08rem;
  box-sizing: border-box;
  background: var(--cat-bar-bg);
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--cat-bar-start), var(--cat-bar-end));
  width: 0%;
  animation: fill-bar 2.8s steps(18) infinite;
}

@keyframes fill-bar { 0% { width: 0%; } 80%,100% { width: 100%; } }

.loading-label {
  font-family: 'Cascadia Mono', Menlo, Monaco, Consolas, monospace;
  font-size: 0.64rem;
  color: var(--cat-loading-label);
  font-weight: bold;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.loading-sub {
  font-size: 0.58rem;
  letter-spacing: 0.08em;
  color: var(--cat-loading-sub);
  font-family: 'Cascadia Mono', Menlo, Monaco, Consolas, monospace;
}

.status-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.status-card--corner {
  position: relative;
  width: clamp(14rem, 22vw, 18rem);
  align-items: flex-start;
  box-sizing: border-box;
  padding: .85rem 1rem;
  border-radius: 1rem;
  border: 1px solid var(--cat-status-border);
  background: linear-gradient(140deg, var(--cat-status-start), var(--cat-status-end));
  backdrop-filter: blur(14px);
  box-shadow: var(--cat-status-shadow);
  overflow: hidden;
}

.status-expand-trigger {
  position: absolute;
  top: 0.7rem;
  right: 0.8rem;
  border: 1px solid var(--cat-thinking-border);
  border-radius: 999px;
  background: color-mix(in srgb, var(--cat-thinking-bg) 88%, rgba(255, 255, 255, 0.12));
  color: var(--cat-stage-text);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 0.28rem 0.58rem;
  cursor: pointer;
  transition: transform 0.16s ease, background 0.16s ease, border-color 0.16s ease;
}

.status-expand-trigger:hover {
  transform: translateY(-1px);
}

.status-text {
  margin-top: 0;
  color: var(--cat-status-text);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;
  animation: pulse-txt 1.8s infinite;
}

@keyframes pulse-txt { 0%,100% { opacity: .5; } 50% { opacity: 1; } }

.stage-text {
  margin-top: .3rem;
  color: var(--cat-stage-text);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .04em;
}

.thinking-box {
  margin-top: .6rem;
  width: min(680px, 92vw);
  max-height: 280px;
  overflow-y: auto;
  border-radius: .9rem;
  border: 1px solid var(--cat-thinking-border);
  background: var(--cat-thinking-bg);
  backdrop-filter: blur(12px);
  padding: .7rem .8rem;
  scrollbar-width: thin;
  scrollbar-color: var(--cat-thinking-scrollbar) transparent;
}

.thinking-box--corner {
  margin-top: .5rem;
  width: 100%;
  max-height: 7rem;
  padding: .65rem .8rem;
  border-radius: .75rem;
  background: color-mix(in srgb, var(--cat-thinking-bg) 90%, rgba(255, 255, 255, 0.08));
  box-sizing: border-box;
}

.thinking-box--expandable {
  cursor: zoom-in;
  transition: border-color 0.16s ease, transform 0.16s ease, box-shadow 0.16s ease;
}

.thinking-box--expandable:hover,
.thinking-box--expandable:focus-visible {
  border-color: var(--cat-stage-text);
  box-shadow: 0 10px 26px rgba(14, 116, 144, 0.12);
  outline: none;
}

.thinking-content {
  font-family: 'Cascadia Mono', Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
  color: var(--cat-thinking-text);
  white-space: pre-wrap;
  word-break: break-all;
}

.expanded-preview-panel {
  width: clamp(24rem, 42vw, 42rem);
  max-width: min(92vw, 42rem);
  max-height: min(62vh, 34rem);
  display: flex;
  flex-direction: column;
  align-self: flex-end;
  border-radius: 1.25rem;
  border: 1px solid var(--cat-status-border);
  background: linear-gradient(145deg, var(--cat-status-start), var(--cat-status-end));
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.28);
  overflow: hidden;
  pointer-events: auto;
}

.expanded-preview-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.1rem 0.9rem;
  border-bottom: 1px solid var(--cat-thinking-border);
}

.expanded-preview-kicker {
  margin: 0 0 0.25rem;
  color: var(--cat-stage-text);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.22em;
}

.expanded-preview-title {
  margin: 0;
  color: var(--cat-status-text);
  font-size: 18px;
  font-weight: 700;
}

.expanded-preview-stage {
  margin: 0.35rem 0 0;
  color: var(--cat-stage-text);
  font-size: 13px;
  font-weight: 600;
}

.expanded-preview-close {
  flex-shrink: 0;
  border: 1px solid var(--cat-thinking-border);
  border-radius: 999px;
  background: transparent;
  color: var(--cat-status-text);
  font-size: 12px;
  font-weight: 700;
  padding: 0.45rem 0.8rem;
  cursor: pointer;
}

.expanded-thinking-box {
  flex: 1;
  overflow: auto;
  padding: 1rem 1.1rem 1.15rem;
  background: color-mix(in srgb, var(--cat-thinking-bg) 92%, rgba(255, 255, 255, 0.06));
}

@media (max-width: 640px) {
  .cat-shell--corner {
    inset: .75rem .75rem auto .75rem;
  }

  .cat-shell__inner--corner {
    gap: .85rem;
    align-items: stretch;
  }

  .matrix-panel {
    width: min(95vw, 22rem);
  }

  .matrix-panel--corner {
    width: min(95vw, 19rem);
  }

  .display-frame {
    min-height: 10rem;
  }

  .matrix-panel--corner .display-frame {
    min-height: 8.1rem;
  }

  .status-card--corner {
    width: min(20rem, 100%);
  }

  .expanded-preview-panel {
    width: min(92vw, 24rem);
    max-height: min(56vh, 26rem);
  }

  .thinking-box--corner {
    width: 100%;
  }
}
</style>
