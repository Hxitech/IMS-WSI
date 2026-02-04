<template>
  <div>
    <div ref="host" style="width: 100%; height: 75vh; border: 1px solid #ddd;"></div>
    <p style="color:#666; font-size: 12px; margin-top: 8px;">
      Tile-based OpenSeadragon viewer (FastAPI + OpenSlide). Tiles are cached under <code>storage/tiles/</code>.
    </p>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import OpenSeadragon from 'openseadragon'

const props = defineProps({
  slideInfo: { type: Object, default: null }
})

const host = ref(null)
let viewer = null

function buildTileSource(info) {
  const tileSize = info.tileSize || 256
  const levels = info.levels || []

  // OpenSeadragon expects maxLevel at full resolution; we map that to API level=0.
  const maxLevel = Math.max(0, levels.length - 1)

  return {
    width: info.width,
    height: info.height,
    tileSize,
    minLevel: 0,
    maxLevel,

    // Map OSD level (0..max, where max is highest resolution) to API OpenSlide level.
    // apiLevel = (maxLevel - osdLevel)
    getTileUrl: function (osdLevel, x, y) {
      const apiLevel = maxLevel - osdLevel
      return `/api/slides/${info.id}/tile/${apiLevel}/${x}/${y}.jpg?tileSize=${tileSize}`
    }
  }
}

function init() {
  if (!host.value) return
  if (viewer) {
    viewer.destroy()
    viewer = null
  }
  if (!props.slideInfo) return

  viewer = OpenSeadragon({
    element: host.value,
    prefixUrl: 'https://openseadragon.github.io/openseadragon/images/',
    showNavigator: true,
    maxZoomPixelRatio: 2,
    tileSources: [buildTileSource(props.slideInfo)]
  })
}

onMounted(init)
watch(() => props.slideInfo, init)

onBeforeUnmount(() => {
  if (viewer) viewer.destroy()
})
</script>
