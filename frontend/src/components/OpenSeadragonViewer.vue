<template>
  <div>
    <div ref="host" style="width: 100%; height: 70vh; border: 1px solid #ddd;"></div>
    <p style="color:#666; font-size: 12px;">
      OpenSeadragon viewer. You can load a plain image URL (MVP) or later switch to DZI/tiles.
    </p>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import OpenSeadragon from 'openseadragon'

const props = defineProps({
  tileSourceUrl: { type: String, default: '' }
})

const host = ref(null)
let viewer = null

function init() {
  if (!host.value) return
  if (viewer) viewer.destroy()
  viewer = OpenSeadragon({
    element: host.value,
    prefixUrl: 'https://openseadragon.github.io/openseadragon/images/',
    tileSources: props.tileSourceUrl ? [props.tileSourceUrl] : []
  })
}

onMounted(init)
watch(() => props.tileSourceUrl, init)

onBeforeUnmount(() => {
  if (viewer) viewer.destroy()
})
</script>
