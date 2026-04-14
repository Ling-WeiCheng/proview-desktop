<script setup lang="ts">
import { BookOpen, FileText, Download, Sparkles } from 'lucide-vue-next'
</script>

<template>
  <div class="fade-in min-h-full">
    <div class="mb-8">
      <h2 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl dark:text-white">
        面经总结
      </h2>
      <p class="mt-2 text-sm font-medium text-slate-500 dark:text-slate-400">AI 自动提炼面试要点，生成结构化面经</p>
    </div>

    <div class="relative rounded-3xl border border-slate-200/60 bg-white/70 p-8 shadow-xl backdrop-blur-xl sm:p-12 dark:border-white/10 dark:bg-[#0A0A0F]/60">
      <div class="flex flex-col items-center text-center max-w-md mx-auto">
        <div class="w-20 h-20 rounded-2xl bg-primary/10 dark:bg-primary/20 flex items-center justify-center mb-6">
          <BookOpen class="w-10 h-10 text-primary" />
        </div>

        <h3 class="text-xl font-bold text-slate-800 dark:text-white mb-3">功能开发中，敬请期待</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-8 leading-relaxed">
          面经总结功能正在紧锣密鼓地开发中，完成后将为你提供以下能力：
        </p>

        <div class="w-full space-y-4 text-left">
          <div class="flex items-start gap-3 p-4 rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5">
            <Sparkles class="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
            <div>
              <div class="text-sm font-bold text-slate-700 dark:text-slate-300">AI 自动提炼面试要点</div>
              <div class="text-xs text-slate-500 dark:text-slate-400 mt-1">智能分析面试对话，提取核心知识点和高频考点</div>
            </div>
          </div>
          <div class="flex items-start gap-3 p-4 rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5">
            <FileText class="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
            <div>
              <div class="text-sm font-bold text-slate-700 dark:text-slate-300">生成结构化面经</div>
              <div class="text-xs text-slate-500 dark:text-slate-400 mt-1">按题型、难度、知识领域自动归类整理</div>
            </div>
          </div>
          <div class="flex items-start gap-3 p-4 rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5">
            <Download class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
            <div>
              <div class="text-sm font-bold text-slate-700 dark:text-slate-300">支持 Markdown 导出</div>
              <div class="text-xs text-slate-500 dark:text-slate-400 mt-1">一键导出面经文档，方便复习和分享</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
