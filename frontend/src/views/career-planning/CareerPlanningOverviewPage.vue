<script setup lang="ts">
import CareerOverviewHero from '../../components/career-planning/CareerOverviewHero.vue'
import { useCareerPlanningStore } from '../../stores/careerPlanning'

const store = useCareerPlanningStore()

async function handleRefresh() {
  try {
    await store.loadDashboard({ force: true })
  } catch (error) {
    store.error = error instanceof Error ? error.message : '刷新职业规划失败'
  }
}

async function handleGenerate() {
  try {
    await store.createPlan({
      target_role: store.targetRole,
      career_goal: store.careerGoal,
      horizon_months: store.horizonMonths,
      refresh: true,
    })
  } catch (error) {
    store.error = error instanceof Error ? error.message : '生成职业规划失败'
  }
}
</script>

<template>
  <section class="space-y-4">
    <CareerOverviewHero
      :profile="store.profile"
      :stats="store.stats"
      :target-role="store.targetRole"
      :career-goal="store.careerGoal"
      :horizon-months="store.horizonMonths"
      :generating="store.generating"
      @update:target-role="store.targetRole = $event"
      @update:career-goal="store.careerGoal = $event"
      @update:horizon-months="store.horizonMonths = $event"
      @refresh="handleRefresh"
      @generate="handleGenerate"
    />
  </section>
</template>