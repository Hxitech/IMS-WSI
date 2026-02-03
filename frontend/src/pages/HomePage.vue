<template>
  <div>
    <h2>Cases</h2>
    <form @submit.prevent="create">
      <input v-model="title" placeholder="New case title" />
      <button type="submit">Create</button>
    </form>

    <ul>
      <li v-for="c in cases" :key="c.id">
        <RouterLink :to="`/cases/${c.id}`">#{{ c.id }} {{ c.title }}</RouterLink>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'

const cases = ref([])
const title = ref('')

async function load() {
  cases.value = (await api.get('/cases')).data
}

async function create() {
  if (!title.value.trim()) return
  await api.post('/cases', { title: title.value, description: null })
  title.value = ''
  await load()
}

onMounted(load)
</script>
