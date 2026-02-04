<template>
  <div v-if="open" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3 style="margin:0;">Columns</h3>
        <button @click="emit('close')">Close</button>
      </div>

      <div style="margin: 10px 0;">
        <button @click="selectAll">Select all</button>
        <button @click="clearAll" style="margin-left:8px;">Clear all</button>
      </div>

      <div class="cols">
        <label v-for="c in columns" :key="c.key" class="col-item">
          <input type="checkbox" :checked="modelValue.includes(c.key)" @change="toggle(c.key)" />
          <span>{{ c.label }}</span>
        </label>
      </div>

      <div class="modal-footer">
        <small style="color:#666;">Saved per user</small>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  open: Boolean,
  columns: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'close'])

function toggle (key) {
  const set = new Set(props.modelValue)
  if (set.has(key)) set.delete(key)
  else set.add(key)
  emit('update:modelValue', Array.from(set))
}

function selectAll () {
  emit('update:modelValue', props.columns.map(c => c.key))
}

function clearAll () {
  emit('update:modelValue', [])
}
</script>

<style scoped>
.modal-backdrop{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display:flex;
  align-items:center;
  justify-content:center;
  z-index: 50;
}
.modal{
  width: 520px;
  max-width: calc(100vw - 24px);
  background:#fff;
  border-radius: 10px;
  padding: 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.modal-header{
  display:flex;
  align-items:center;
  justify-content:space-between;
}
.cols{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 8px;
}
.col-item{
  display:flex;
  gap: 8px;
  align-items:center;
  padding: 6px;
  border: 1px solid #eee;
  border-radius: 8px;
}
.modal-footer{
  margin-top: 12px;
  display:flex;
  justify-content:flex-end;
}
</style>
