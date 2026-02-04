<template>
  <div>
    <div style="display:flex; align-items:center; gap:12px; margin-bottom: 8px;">
      <h2 style="margin:0;">Slide Viewer</h2>
      <span v-if="info" style="color:#666; font-size:12px;">#{{ info.id }} — {{ info.label }}</span>
    </div>

    <div v-if="error" style="color:#b00; margin-bottom: 8px;">{{ error }}</div>
    <div v-if="!info && !error" style="color:#666;">Loading…</div>

    <OpenSeadragonViewer v-if="info" :slideInfo="info" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import OpenSeadragonViewer from '../components/OpenSeadragonViewer.vue'

const route = useRoute()
const info = ref(null)
const error = ref('')

onMounted(async () => {
  const id = route.params.slideId
  try {
    const resp = await fetch(`/api/slides/${id}/info`)
    if (!resp.ok) throw new Error(`Failed to load slide info (${resp.status})`)
    info.value = await resp.json()
  } catch (e) {
    error.value = e?.message || String(e)
  }
})
</script>
