<template>
  <div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; padding: 16px;">
    <h1>App</h1>
    <nav style="display:flex; gap:12px; margin-bottom: 16px;">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/viewer">Viewer</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>
