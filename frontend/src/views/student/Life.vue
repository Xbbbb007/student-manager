<script setup lang="ts">
import Attendance from "./Attendance.vue";
</script>

<template>
  <div class="student-life-page">
    <div class="life-body">
      <Attendance />
    </div>
  </div>
</template>

<style scoped>
.student-life-page {
  padding: 30px var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
}
.life-body {
  background: var(--color-bg-content);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
  min-height: 480px;
}
</style>
