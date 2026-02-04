<template>
  <div>
    <div style="display:flex; align-items:center; justify-content:space-between; gap: 12px;">
      <h2 style="margin:0;">Cases</h2>
      <div style="display:flex; gap: 8px; align-items:center;">
        <input v-model="q" placeholder="Search cases..." @keyup.enter="load" />
        <label style="font-size: 13px; color:#444;">
          <input type="checkbox" v-model="showArchived" @change="load" />
          Show archived
        </label>
        <button @click="openCols=true">Columns</button>
      </div>
    </div>

    <ColumnConfigModal
      :open="openCols"
      :columns="columns"
      v-model="visible"
      @close="openCols=false"
    />

    <form @submit.prevent="create" style="margin: 12px 0; display:flex; gap: 8px;">
      <input v-model="title" placeholder="New case title" style="flex: 1;" />
      <button type="submit">Create</button>
    </form>

    <DataTable
      :columns="columns"
      :visible-keys="visible"
      :rows="cases"
      :sort-key="sort"
      :sort-order="order"
      @update:sort="onSort"
    >
      <template #cell:id="{ row, value }">
        <RouterLink :to="`/cases/${row.id}`">#{{ value }}</RouterLink>
      </template>

      <template #cell:created_at="{ value }">
        <span style="font-size: 12px; color:#666;">{{ fmtDate(value) }}</span>
      </template>
    </DataTable>

    <div style="margin-top: 10px; display:flex; align-items:center; justify-content:space-between; color:#666; font-size: 12px;">
      <div>Total: {{ total }}</div>
      <button @click="load">Refresh</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import DataTable from '../components/DataTable.vue'
import ColumnConfigModal from '../components/ColumnConfigModal.vue'
import { listCases, createCase, getListPref, setListPref } from '../services/api'

const cases = ref([])
const total = ref(0)

const title = ref('')
const q = ref('')
const showArchived = ref(false)

const sort = ref('id')
const order = ref('desc')

const openCols = ref(false)

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'description', label: 'Description', sortable: false },
  { key: 'slide_count', label: 'Slides', sortable: true },
  { key: 'is_archived', label: 'Archived', sortable: true },
  { key: 'created_at', label: 'Created', sortable: true }
]

const visible = ref(['id', 'title', 'slide_count', 'created_at'])

async function loadPrefs () {
  const res = await getListPref('cases_columns')
  if (res?.value?.length) visible.value = res.value
}

watch(visible, async (v) => {
  await setListPref('cases_columns', v)
}, { deep: true })

async function load () {
  const params = {
    q: q.value || undefined,
    is_archived: showArchived.value ? undefined : false,
    sort: sort.value,
    order: order.value,
    limit: 200,
    offset: 0
  }
  const res = await listCases(params)
  cases.value = res.items
  total.value = res.total
}

function onSort (s) {
  sort.value = s.sort
  order.value = s.order
  load()
}

async function create () {
  if (!title.value.trim()) return
  await createCase({ title: title.value, description: null })
  title.value = ''
  await load()
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
