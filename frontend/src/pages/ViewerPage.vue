<template>
  <div>
    <h2>Viewer</h2>
    <div style="margin-bottom: 8px;">
      <input v-model="url" style="width: 100%;" placeholder="Paste image URL (e.g. backend /files/.../thumb.jpg)" />
    </div>
    <OpenSeadragonViewer :tileSourceUrl="url" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import OpenSeadragonViewer from '../components/OpenSeadragonViewer.vue'

const url = ref('')
</script>
