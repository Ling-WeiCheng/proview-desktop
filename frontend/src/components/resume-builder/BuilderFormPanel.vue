<script setup lang="ts">
import BuilderHeader from './BuilderHeader.vue'
import TemplateGallery from './TemplateGallery.vue'
import BasicInfoForm from './BasicInfoForm.vue'
import ModuleList from './ModuleList.vue'
</script>

<template>
  <div class="glass-panel rounded-3xl flex flex-col overflow-y-auto h-full custom-scroll">
    <div class="p-5 space-y-5">
      <!-- Mode selector -->
      <BuilderHeader />

      <!-- Template & style settings -->
      <TemplateGallery />

      <!-- Basic info form -->
      <BasicInfoForm />

      <!-- Module list -->
      <ModuleList />
    </div>
  </div>
</template>
