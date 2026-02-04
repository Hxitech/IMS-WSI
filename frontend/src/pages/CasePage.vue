<template>
  <div>
    <h2>Case {{ id }}</h2>

    <section style="margin-bottom: 16px;">
      <h3>Slides</h3>
      <div style="margin: 8px 0;">
        <input ref="fileInput" type="file" @change="onUploadSlide" />
        <span v-if="uploading" style="margin-left: 8px;">Uploading...</span>
      </div>
      <ul>
        <li v-for="s in slides" :key="s.id" style="margin: 8px 0;">
          <div>
            #{{ s.id }} {{ s.label }}
            <span v-if="s.filename"> — {{ s.filename }}</span>
            <span v-if="s.ingested_ok" style="color: green;"> [ingested]</span>
            <span v-else style="color: #999;"> [not ingested]</span>
          </div>
          <div v-if="thumbSrc(s)" style="margin-top: 4px;">
            <img :src="thumbSrc(s)" alt="thumb" style="max-width: 280px; border: 1px solid #eee;" />
            <div style="font-size: 12px; color: #666;">
              {{ s.width }}x{{ s.height }} levels={{ s.level_count }} mpp={{ s.mpp_x }}
            </div>
          </div>
        </li>
      </ul>
    </section>

    <section>
      <h3>Tasks</h3>
      <form @submit.prevent="createTaskAction">
        <input v-model="taskTitle" placeholder="New task" />
        <button type="submit">Add</button>
      </form>
      <ul>
        <li v-for="t in tasks" :key="t.id">#{{ t.id }} {{ t.title }} — {{ t.status }}</li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { listSlides, listTasks, createTask, uploadSlide, fileUrl } from '../services/api'

const props = defineProps({ id: String })
const id = Number(props.id)

const slides = ref([])
const tasks = ref([])
const taskTitle = ref('')

const uploading = ref(false)
const fileInput = ref(null)

async function load() {
  slides.value = await listSlides(id)
  tasks.value = await listTasks(id)
}

async function createTaskAction() {
  if (!taskTitle.value.trim()) return
  await createTask({ case_id: id, title: taskTitle.value, notes: null })
  taskTitle.value = ''
  await load()
}

async function onUploadSlide(e) {
  const f = e?.target?.files?.[0]
  if (!f) return
  uploading.value = true
  try {
    await uploadSlide(id, f)
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
  await load()
}

function thumbSrc(s) {
  return s.thumb_path ? fileUrl(s.thumb_path) : null
}

onMounted(load)
</script>
