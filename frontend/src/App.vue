<script setup lang="ts">
</script>

<template>
  <router-view />
</template>

<style>
.page-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: var(--color-bg-white);
  border-radius: var(--radius-md);
  border: 2px dashed var(--color-border);
  color: var(--color-text-secondary);
}

.page-placeholder h2 {
  font-size: var(--font-size-xl);
  margin-bottom: 8px;
  color: var(--color-text);
}

.page-placeholder .text-secondary {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
</style>
