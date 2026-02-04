<template>
  <table class="tbl">
    <thead>
      <tr>
        <th v-for="c in visibleColumns" :key="c.key" @click="onSort(c)" :class="{sortable: c.sortable}">
          <span>{{ c.label }}</span>
          <span v-if="sortKey===c.key" style="margin-left:6px;">{{ sortOrder==='asc' ? '▲' : '▼' }}</span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in rows" :key="rowKey(row)">
        <td v-for="c in visibleColumns" :key="c.key">
          <slot :name="`cell:${c.key}`" :row="row" :value="row[c.key]">
            {{ format(row[c.key]) }}
          </slot>
        </td>
      </tr>
      <tr v-if="rows.length===0">
        <td :colspan="visibleColumns.length" style="padding:12px; color:#777;">No results</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: { type: Array, default: () => [] },
  visibleKeys: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] },
  rowKeyFn: { type: Function, default: (r) => r.id },
  sortKey: { type: String, default: 'id' },
  sortOrder: { type: String, default: 'desc' }
})
const emit = defineEmits(['update:sort'])

const visibleColumns = computed(() => {
  const set = new Set(props.visibleKeys)
  return props.columns.filter(c => set.has(c.key))
})

function rowKey (row) {
  return props.rowKeyFn(row)
}

function onSort (col) {
  if (!col.sortable) return
  let order = 'asc'
  if (props.sortKey === col.key) order = props.sortOrder === 'asc' ? 'desc' : 'asc'
  emit('update:sort', { sort: col.key, order })
}

function format (v) {
  if (v === null || v === undefined) return ''
  return String(v)
}
</script>

<style scoped>
.tbl{
  width:100%;
  border-collapse: collapse;
}
th, td{
  border-bottom: 1px solid #eee;
  padding: 8px;
  text-align:left;
  font-size: 14px;
}
th.sortable{ cursor:pointer; user-select:none; }
</style>
