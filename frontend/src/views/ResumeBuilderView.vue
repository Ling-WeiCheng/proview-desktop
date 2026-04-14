<script setup lang="ts">
import { defineAsyncComponent, onMounted } from 'vue'
import { useResumeBuilderStore } from '../stores/resumeBuilder'
import CatLoading from '../components/CatLoading.vue'

const store = useResumeBuilderStore()
const AsyncBuilderPreviewPanel = defineAsyncComponent(() => import('../components/resume-builder/BuilderPreviewPanel.vue'))
const AsyncBuilderFormPanel = defineAsyncComponent(() => import('../components/resume-builder/BuilderFormPanel.vue'))
const AsyncPolishDrawer = defineAsyncComponent(() => import('../components/resume-builder/PolishDrawer.vue'))

onMounted(() => {
  if (!store.loadDraft()) {
    store.initBlank()
  }
})
</script>

<template>
  <Suspense>
    <template #default>
      <div class="builder-root">
        <CatLoading
          v-if="store.isPolishing"
          variant="corner"
          :blocking="false"
          :message="'AI \u6b63\u5728\u5206\u6790\u7b80\u5386\u5e76\u751f\u6210\u4f18\u5316\u5efa\u8bae'"
          :stage="'\u4f60\u4ecd\u53ef\u7ee7\u7eed\u7f16\u8f91\u548c\u9884\u89c8'"
        />

        <CatLoading
          v-if="store.phase === 'exporting'"
          variant="corner"
          :blocking="false"
          :message="'\u6b63\u5728\u5bfc\u51fa\u7b80\u5386 PDF'"
          :stage="'\u4f60\u4ecd\u53ef\u7ee7\u7eed\u67e5\u770b\u5f53\u524d\u5185\u5bb9'"
        />

        <AsyncBuilderPreviewPanel class="builder-left" />
        <AsyncBuilderFormPanel class="builder-right" />
        <AsyncPolishDrawer v-if="store.polishDrawerOpen" />
      </div>
    </template>

    <template #fallback>
      <div class="builder-loading-shell">
        <CatLoading
          variant="corner"
          :blocking="false"
          :message="'\u6b63\u5728\u6309\u9700\u52a0\u8f7d\u7b80\u5386\u751f\u6210\u5de5\u4f5c\u53f0'"
          :stage="'\u7f16\u8f91\u5668\u548c AI \u5efa\u8bae\u9762\u677f\u6b63\u5728\u61d2\u52a0\u8f7d'"
        />
      </div>
    </template>
  </Suspense>
</template>

<style scoped>
.builder-root {
  display: flex;
  gap: 16px;
  margin: -2rem -2rem 0;
  padding: 16px;
  height: calc(100vh - 2rem);
  min-height: 0;
}

.builder-loading-shell {
  min-height: calc(100vh - 2rem);
}

.builder-left {
  flex: 1 1 0;
  min-width: 0;
  overflow: hidden;
}

.builder-right {
  width: 380px;
  flex-shrink: 0;
  min-height: 0;
}
</style>
