<template>
  <div>
    <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
      <h2 style="margin:0;">Case {{ id }}</h2>
      <div style="display:flex; gap: 8px; align-items:center;">
        <input v-model="q" placeholder="Search slides..." @keyup.enter="load" />
        <select v-model="processing_status" @change="load">
          <option value="">All statuses</option>
          <option v-for="v in processingStatusOptions" :key="v" :value="v">{{ v }}</option>
        </select>
        <select v-model="review_result" @change="load">
          <option value="">All review</option>
          <option v-for="v in reviewResultOptions" :key="v" :value="v">{{ v }}</option>
        </select>
        <label style="font-size: 13px; color:#444;">
          <input type="checkbox" v-model="showArchived" @change="load" />
          Show archived
        </label>
        <button @click="openCols=true">Columns</button>
      </div>
    </div>

    <section style="margin: 12px 0 16px;">
      <h3>Slides</h3>
      <div style="margin: 8px 0; display:flex; align-items:center; gap: 8px;">
        <input ref="fileInput" type="file" @change="onUploadSlide" />
        <span v-if="uploading" style="margin-left: 8px;">Uploading...</span>
        <button @click="load" style="margin-left:auto;">Refresh</button>
      </div>

      <ColumnConfigModal
        :open="openCols"
        :columns="columns"
        v-model="visible"
        @close="openCols=false"
      />

      <DataTable
        :columns="columns"
        :visible-keys="visible"
        :rows="slides"
        :sort-key="sort"
        :sort-order="order"
        @update:sort="onSort"
      >
        <template #cell:id="{ row, value }">
          <RouterLink :to="`/slides/${row.id}/view`" v-if="row.ingested_ok">#{{ value }}</RouterLink>
          <span v-else>#{{ value }}</span>
        </template>

        <template #cell:thumb_path="{ row }">
          <img v-if="thumbSrc(row)" :src="thumbSrc(row)" alt="thumb" style="max-width: 96px; border: 1px solid #eee;" />
        </template>

        <template #cell:ingested_ok="{ value }">
          <span :style="{color: value ? 'green' : '#999'}">{{ value ? 'yes' : 'no' }}</span>
        </template>

        <template #cell:updated_at="{ value }">
          <span style="font-size: 12px; color:#666;">{{ fmtDate(value) }}</span>
        </template>

        <template #cell:created_at="{ value }">
          <span style="font-size: 12px; color:#666;">{{ fmtDate(value) }}</span>
        </template>
      </DataTable>

      <div style="margin-top: 10px; color:#666; font-size: 12px;">Total: {{ totalSlides }}</div>
    </section>

    <section>
      <h3>Tasks</h3>
      <form @submit.prevent="createTaskAction" style="display:flex; gap: 8px;">
        <input v-model="taskTitle" placeholder="New task" style="flex:1;" />
        <button type="submit">Add</button>
      </form>
      <ul>
        <li v-for="t in tasks" :key="t.id">#{{ t.id }} {{ t.title }} — {{ t.status }}</li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import DataTable from '../components/DataTable.vue'
import ColumnConfigModal from '../components/ColumnConfigModal.vue'
import { listSlides, listTasks, createTask, uploadSlide, fileUrl, getListPref, setListPref } from '../services/api'

const props = defineProps({ id: String })
const id = Number(props.id)

const slides = ref([])
const totalSlides = ref(0)
const tasks = ref([])
const taskTitle = ref('')

const uploading = ref(false)
const fileInput = ref(null)

const q = ref('')
const showArchived = ref(false)

const processing_status = ref('')
const review_result = ref('')

const processingStatusOptions = ['queued', 'running', 'done', 'failed']
const reviewResultOptions = ['pass', 'fail', 'needs_review']

const sort = ref('id')
const order = ref('desc')

const openCols = ref(false)

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'label', label: 'Label', sortable: true },
  { key: 'slide_number', label: 'Slide #', sortable: true },
  { key: 'folder', label: 'Folder', sortable: true },
  { key: 'filename', label: 'Filename', sortable: true },
  { key: 'ai_module', label: 'AI Module', sortable: true },
  { key: 'scan_magnification', label: 'Mag', sortable: true },
  { key: 'processing_status', label: 'Status', sortable: true },
  { key: 'review_result', label: 'Review', sortable: true },
  { key: 'quality', label: 'Quality', sortable: true },
  { key: 'clarity', label: 'Clarity', sortable: true },
  { key: 'ingested_ok', label: 'Ingested', sortable: true },
  { key: 'thumb_path', label: 'Thumb', sortable: false },
  { key: 'updated_at', label: 'Updated', sortable: true },
  { key: 'created_at', label: 'Created', sortable: true }
]

const visible = ref(['id', 'label', 'filename', 'processing_status', 'review_result', 'ingested_ok', 'thumb_path'])

async function loadPrefs () {
  const res = await getListPref('slides_columns')
  if (res?.value?.length) visible.value = res.value
}

watch(visible, async (v) => {
  await setListPref('slides_columns', v)
}, { deep: true })

async function load () {
  const params = {
    q: q.value || undefined,
    is_archived: showArchived.value ? undefined : false,
    processing_status: processing_status.value || undefined,
    review_result: review_result.value || undefined,
    sort: sort.value,
    order: order.value,
    limit: 200,
    offset: 0
  }
  const res = await listSlides(id, params)
  slides.value = res.items
  totalSlides.value = res.total
  tasks.value = await listTasks(id)
}

function onSort (s) {
  sort.value = s.sort
  order.value = s.order
  load()
}

async function createTaskAction () {
  if (!taskTitle.value.trim()) return
  await createTask({ case_id: id, title: taskTitle.value, notes: null })
  taskTitle.value = ''
  await load()
}

async function onUploadSlide (e) {
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

function thumbSrc (s) {
  return s.thumb_path ? fileUrl(s.thumb_path) : null
}

function fmtDate (v) {
  if (!v) return ''
  try { return new Date(v).toLocaleString() } catch { return String(v) }
}

onMounted(async () => {
  await loadPrefs()
  await load()
})
</script>
