<template>
  <div>
    <h2>Case {{ id }}</h2>

    <section style="margin-bottom: 16px;">
      <h3>Slides</h3>
      <ul>
        <li v-for="s in slides" :key="s.id">
          #{{ s.id }} {{ s.label }} <span v-if="s.dzi_path">(dzi: {{ s.dzi_path }})</span>
        </li>
      </ul>
    </section>

    <section>
      <h3>Tasks</h3>
      <form @submit.prevent="createTask">
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
import api from '../services/api'

const props = defineProps({ id: String })
const id = Number(props.id)

const slides = ref([])
const tasks = ref([])
const taskTitle = ref('')

async function load() {
  slides.value = (await api.get(`/cases/${id}/slides`)).data
  tasks.value = (await api.get(`/cases/${id}/tasks`)).data
}

async function createTask() {
  if (!taskTitle.value.trim()) return
  await api.post('/tasks', { case_id: id, title: taskTitle.value, notes: null })
  taskTitle.value = ''
  await load()
}

onMounted(load)
</script>
