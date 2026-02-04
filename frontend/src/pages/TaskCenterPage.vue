<template>
  <div>
    <div style="display:flex; align-items:center; justify-content:space-between; gap: 12px;">
      <div>
        <h2 style="margin:0;">Task Center</h2>
        <div style="color:#666; font-size: 13px;">Manage assignments (manual / by-count / by-time).</div>
      </div>

      <div style="display:flex; align-items:center; gap:10px;">
        <div v-if="me" style="font-size: 13px; color:#333;">
          Signed in as <b>{{ me.username }}</b> ({{ me.role }})
        </div>
        <button @click="onLogout" style="padding:8px 10px; cursor:pointer;">Logout</button>
      </div>
    </div>

    <div style="display:flex; gap: 16px; flex-wrap: wrap; margin-top: 16px;">
      <div style="border: 1px solid #ddd; padding: 12px; border-radius: 8px; min-width: 280px;">
        <div style="font-weight: 600;">Auto-assign defaults</div>
        <div style="display:flex; gap:10px; margin-top: 10px; align-items:center;">
          <label style="font-size: 13px;">Eligible role
            <select v-model="eligibleRole" style="margin-left: 8px; padding:6px;">
              <option value="tech">tech</option>
              <option value="doctor">doctor</option>
            </select>
          </label>
          <label style="font-size: 13px;">Lookback (min)
            <input v-model.number="lookbackMinutes" type="number" min="1" style="margin-left: 8px; width: 90px; padding:6px;" />
          </label>
        </div>
        <div style="color:#666; font-size: 12px; margin-top: 8px;">
          by-count = fewest open tasks. by-time = fewest assignments within lookback.
        </div>
      </div>

      <div style="border: 1px solid #ddd; padding: 12px; border-radius: 8px; min-width: 280px;">
        <div style="font-weight: 600;">Assignable users</div>
        <div style="margin-top: 10px; display:flex; gap: 8px;">
          <button @click="loadUsers" style="padding:8px 10px; cursor:pointer;">Refresh users</button>
          <span style="color:#666; font-size: 12px; align-self:center;">{{ users.length }} active</span>
        </div>
        <div style="margin-top: 10px; max-height: 120px; overflow:auto; font-size: 13px;">
          <div v-for="u in users" :key="u.id" style="display:flex; justify-content:space-between; padding:4px 0; border-bottom: 1px dashed #eee;">
            <span>{{ u.username }}</span>
            <span style="color:#666;">{{ u.role }}</span>
          </div>
        </div>
      </div>
    </div>

    <div style="margin-top: 18px;">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:10px;">
        <div style="font-weight: 700;">Tasks</div>
        <div style="display:flex; gap: 8px;">
          <button @click="loadTasks" style="padding:8px 10px; cursor:pointer;">Refresh tasks</button>
        </div>
      </div>

      <div v-if="error" style="color:#b00020; margin-top: 10px;">{{ error }}</div>

      <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
          <tr>
            <th style="text-align:left; border-bottom:1px solid #ddd; padding: 8px;">ID</th>
            <th style="text-align:left; border-bottom:1px solid #ddd; padding: 8px;">Title</th>
            <th style="text-align:left; border-bottom:1px solid #ddd; padding: 8px;">Status</th>
            <th style="text-align:left; border-bottom:1px solid #ddd; padding: 8px;">Assignee</th>
            <th style="text-align:left; border-bottom:1px solid #ddd; padding: 8px;">Strategy</th>
            <th style="text-align:left; border-bottom:1px solid #ddd; padding: 8px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tasks" :key="t.id">
            <td style="padding: 8px; border-bottom:1px solid #f0f0f0;">{{ t.id }}</td>
            <td style="padding: 8px; border-bottom:1px solid #f0f0f0;">{{ t.title }}</td>
            <td style="padding: 8px; border-bottom:1px solid #f0f0f0;">{{ t.status }}</td>
            <td style="padding: 8px; border-bottom:1px solid #f0f0f0;">
              <select v-model.number="manualAssignee[t.id]" style="padding:6px;">
                <option :value="null">(unassigned)</option>
                <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }} ({{ u.role }})</option>
              </select>
            </td>
            <td style="padding: 8px; border-bottom:1px solid #f0f0f0; color:#555;">
              {{ t.assign_strategy || '-' }}
            </td>
            <td style="padding: 8px; border-bottom:1px solid #f0f0f0;">
              <div style="display:flex; gap: 8px; flex-wrap: wrap;">
                <button @click="manualAssign(t.id)" style="padding:6px 8px; cursor:pointer;">Manual assign</button>
                <button @click="autoAssign(t.id, 'by_count')" style="padding:6px 8px; cursor:pointer;">Auto by-count</button>
                <button @click="autoAssign(t.id, 'by_time')" style="padding:6px 8px; cursor:pointer;">Auto by-time</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="tasks.length === 0" style="color:#666; margin-top: 10px;">No tasks found.</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'
import { api } from '../services/api'
import { clearAuth, fetchMe, getUser } from '../services/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const me = ref(getUser())

const tasks = ref([])
const users = ref([])
const manualAssignee = reactive({})
const eligibleRole = ref('tech')
const lookbackMinutes = ref(120)
const error = ref('')

async function loadMe () {
  try {
    me.value = await fetchMe()
  } catch (e) {
    // token invalid
    await router.push('/login')
  }
}

async function loadUsers () {
  users.value = await api.get('/task-center/users').then(r => r.data)
}

async function loadTasks () {
  tasks.value = await api.get('/task-center/tasks').then(r => r.data)
  for (const t of tasks.value) {
    if (!(t.id in manualAssignee)) manualAssignee[t.id] = t.assignee_id ?? null
  }
}

async function manualAssign (taskId) {
  error.value = ''
  try {
    const assignee_id = manualAssignee[taskId]
    await api.post(`/task-center/tasks/${taskId}/assign`, { assignee_id })
    await loadTasks()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Assignment failed'
  }
}

async function autoAssign (taskId, strategy) {
  error.value = ''
  try {
    await api.post(`/task-center/tasks/${taskId}/auto-assign`, {
      strategy,
      eligible_role: eligibleRole.value,
      lookback_minutes: lookbackMinutes.value
    })
    await loadTasks()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Auto-assign failed'
  }
}

async function onLogout () {
  clearAuth()
  await router.push('/login')
}

onMounted(async () => {
  await loadMe()
  await Promise.all([loadUsers(), loadTasks()])
})
</script>
