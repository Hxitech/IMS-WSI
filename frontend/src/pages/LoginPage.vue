<template>
  <div style="max-width: 420px;">
    <h2>Login</h2>
    <p style="color:#666; margin-top: -8px;">Use your username + password.</p>

    <div style="display:flex; flex-direction:column; gap:10px; margin-top: 12px;">
      <label>
        <div style="font-size: 12px; color:#555;">Username</div>
        <input v-model="username" style="width:100%; padding:10px;" placeholder="admin" />
      </label>
      <label>
        <div style="font-size: 12px; color:#555;">Password</div>
        <input v-model="password" type="password" style="width:100%; padding:10px;" placeholder="••••••" />
      </label>

      <button @click="onLogin" :disabled="loading" style="padding:10px; cursor:pointer;">
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>

      <div v-if="error" style="color: #b00020;">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/auth'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function onLogin () {
  error.value = ''
  loading.value = true
  try {
    await login(username.value, password.value)
    await router.push('/task-center')
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
