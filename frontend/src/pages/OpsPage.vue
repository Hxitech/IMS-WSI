<template>
  <div style="max-width: 980px;">
    <h2>Ops</h2>
    <p style="margin-top: -6px; color: #555;">Admin-only storage monitoring, cleanup, trash management, and export.</p>

    <div v-if="!isAdmin" style="padding: 12px; border: 1px solid #f0c36d; background:#fff7e6; border-radius: 8px;">
      <b>Forbidden</b>
      <div style="color:#555;">You must be an admin to access Ops.</div>
    </div>

    <div v-else>
      <!-- Storage card -->
      <section style="border:1px solid #eee; border-radius: 10px; padding: 14px; margin: 14px 0;">
        <div style="display:flex; justify-content: space-between; align-items: baseline; gap: 12px;">
          <h3 style="margin: 0;">Storage</h3>
          <button @click="loadStorage" :disabled="loading.storage" style="padding:8px 10px;">Refresh</button>
        </div>

        <div v-if="storage" style="margin-top: 10px;">
          <div style="display:flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap;">
            <div>
              <div style="font-size: 13px; color:#666;">Root</div>
              <code>{{ storage.storage_root }}</code>
            </div>
            <div style="text-align:right;">
              <div style="font-size: 13px; color:#666;">Used</div>
              <div style="font-size: 18px; font-weight: 700;" :style="{ color: storage.warn ? '#b00020' : '#111' }">
                {{ storage.used_percent }}% ({{ storage.used_h }} / {{ storage.total_h }})
              </div>
              <div style="font-size: 12px; color:#666;">Warn at {{ storage.warn_threshold_percent }}%</div>
            </div>
          </div>

          <div style="height: 10px; background:#f3f3f3; border-radius: 999px; overflow:hidden; margin-top: 10px;">
            <div
              :style="{
                width: Math.min(100, storage.used_percent) + '%',
                height: '100%',
                background: storage.warn ? '#d32f2f' : '#1976d2'
              }"
            />
          </div>

          <div style="margin-top: 8px; color:#666; font-size: 13px;">
            Free: <b>{{ storage.free_h }}</b>
          </div>
        </div>

        <div v-else style="margin-top: 10px; color:#666;">No data yet.</div>
      </section>

      <!-- Cleanup -->
      <section style="border:1px solid #eee; border-radius: 10px; padding: 14px; margin: 14px 0;">
        <h3 style="margin-top: 0;">Cleanup (move to trash)</h3>

        <div style="display:flex; gap: 18px; flex-wrap: wrap; align-items: center;">
          <label style="display:flex; gap: 8px; align-items:center;">
            <input type="checkbox" v-model="cleanup.include_tiles" />
            Tiles cache (<code>storage/tiles</code>)
          </label>
          <label style="display:flex; gap: 8px; align-items:center;">
            <input type="checkbox" v-model="cleanup.include_thumbs" />
            Thumbnails (<code>thumb.jpg</code>)
          </label>
          <label style="display:flex; gap: 8px; align-items:center;">
            <input type="checkbox" v-model="cleanup.include_raw" />
            Raw slide files (<code>slides/*/*/raw</code>)
          </label>
        </div>

        <div style="margin-top: 10px; display:flex; gap: 10px; align-items:center;">
          <button @click="runCleanup" :disabled="loading.cleanup" style="padding:8px 10px;">Run cleanup</button>
          <span v-if="lastCleanup" style="color:#555;">Moved {{ lastCleanup.moved_paths.length }} path(s) to trash.</span>
        </div>

        <details v-if="lastCleanup" style="margin-top: 10px;">
          <summary>Details</summary>
          <pre style="background:#fafafa; border:1px solid #eee; padding: 10px; border-radius: 8px; overflow:auto;">{{ lastCleanup }}</pre>
        </details>
      </section>

      <!-- Trash -->
      <section style="border:1px solid #eee; border-radius: 10px; padding: 14px; margin: 14px 0;">
        <div style="display:flex; justify-content: space-between; align-items: baseline; gap: 12px;">
          <h3 style="margin: 0;">Trash</h3>
          <button @click="loadTrash" :disabled="loading.trash" style="padding:8px 10px;">Refresh</button>
        </div>
        <div v-if="trash" style="margin-top: 10px; color:#555;">
          Total: <b>{{ trash.total_h }}</b> ({{ trash.entries.length }} file(s))
        </div>

        <div v-if="trash && trash.entries.length" style="margin-top: 10px;">
          <div style="display:flex; gap: 10px; align-items:center; flex-wrap: wrap;">
            <button @click="purgeExpired" :disabled="loading.purge" style="padding:8px 10px;">Purge expired</button>
            <button @click="purgeAll" :disabled="loading.purge" style="padding:8px 10px; background:#b00020; color:#fff; border: none; border-radius: 6px;">Purge ALL</button>
            <span style="font-size: 12px; color:#666;">(Default retention: {{ retentionDays }} days)</span>
          </div>

          <table style="width:100%; border-collapse: collapse; margin-top: 10px; font-size: 14px;">
            <thead>
              <tr style="text-align:left; border-bottom: 1px solid #eee;">
                <th style="padding: 8px;">Path</th>
                <th style="padding: 8px; width: 120px;">Size</th>
                <th style="padding: 8px; width: 220px;">Modified (UTC)</th>
                <th style="padding: 8px; width: 190px;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in trash.entries.slice(0, 50)" :key="e.path" style="border-bottom: 1px solid #f3f3f3;">
                <td style="padding: 8px;"><code>{{ e.path }}</code></td>
                <td style="padding: 8px;">{{ e.size_h }}</td>
                <td style="padding: 8px; color:#555;">{{ e.mtime_iso }}</td>
                <td style="padding: 8px; display:flex; gap: 8px;">
                  <button @click="restore(e.path)" :disabled="loading.restore" style="padding:6px 10px;">Restore</button>
                  <button @click="purgePath(e.path)" :disabled="loading.purge" style="padding:6px 10px; background:#eee;">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="trash.entries.length > 50" style="margin-top: 8px; color:#666; font-size: 12px;">Showing first 50 entries.</div>
        </div>
        <div v-else-if="trash" style="margin-top: 10px; color:#666;">Trash is empty.</div>
      </section>

      <!-- Export -->
      <section style="border:1px solid #eee; border-radius: 10px; padding: 14px; margin: 14px 0;">
        <h3 style="margin-top: 0;">Export</h3>
        <div style="color:#555; font-size: 13px;">Copies storage folders to an absolute destination path on the server.</div>

        <div style="margin-top: 10px; display:flex; gap: 10px; align-items:center; flex-wrap: wrap;">
          <input v-model="exportReq.dest_path" placeholder="/mnt/backup/app-storage" style="padding:8px 10px; min-width: 360px;" />
          <button @click="runExport" :disabled="loading.export" style="padding:8px 10px;">Export</button>
        </div>

        <div style="margin-top: 10px; display:flex; gap: 18px; flex-wrap: wrap; align-items: center;">
          <label style="display:flex; gap: 8px; align-items:center;">
            <input type="checkbox" v-model="exportReq.include_raw" /> Raw
          </label>
          <label style="display:flex; gap: 8px; align-items:center;">
            <input type="checkbox" v-model="exportReq.include_thumbs" /> Thumbs
          </label>
          <label style="display:flex; gap: 8px; align-items:center;">
            <input type="checkbox" v-model="exportReq.include_tiles" /> Tiles
          </label>
        </div>

        <details v-if="lastExport" style="margin-top: 10px;">
          <summary>Last export result</summary>
          <pre style="background:#fafafa; border:1px solid #eee; padding: 10px; border-radius: 8px; overflow:auto;">{{ lastExport }}</pre>
        </details>
      </section>

      <div v-if="err" style="padding: 10px; border: 1px solid #f3b4b4; background:#fff0f0; border-radius: 8px; color:#7a0000;">
        {{ err }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { api } from '../services/api'
import { getUser } from '../services/auth'

const user = ref(getUser())
const isAdmin = computed(() => user.value && user.value.role === 'admin')

const retentionDays = 30

const storage = ref(null)
const trash = ref(null)
const err = ref('')

const loading = reactive({
  storage: false,
  cleanup: false,
  trash: false,
  restore: false,
  purge: false,
  export: false
})

const cleanup = reactive({
  include_tiles: true,
  include_thumbs: true,
  include_raw: false
})

const exportReq = reactive({
  dest_path: '/mnt/backup/app-storage',
  include_raw: true,
  include_thumbs: true,
  include_tiles: true
})

const lastCleanup = ref(null)
const lastExport = ref(null)

function setError (e) {
  err.value = (e?.response?.data?.detail) || e?.message || String(e)
}

async function loadStorage () {
  err.value = ''
  loading.storage = true
  try {
    storage.value = await api.get('/ops/storage').then(r => r.data)
  } catch (e) {
    setError(e)
  } finally {
    loading.storage = false
  }
}

async function runCleanup () {
  err.value = ''
  loading.cleanup = true
  try {
    lastCleanup.value = await api.post('/ops/cleanup', cleanup).then(r => r.data)
    await loadTrash()
    await loadStorage()
  } catch (e) {
    setError(e)
  } finally {
    loading.cleanup = false
  }
}

async function loadTrash () {
  err.value = ''
  loading.trash = true
  try {
    trash.value = await api.get('/ops/trash').then(r => r.data)
  } catch (e) {
    setError(e)
  } finally {
    loading.trash = false
  }
}

async function restore (path) {
  err.value = ''
  loading.restore = true
  try {
    await api.post('/ops/trash/restore', { path })
    await loadTrash()
    await loadStorage()
  } catch (e) {
    setError(e)
  } finally {
    loading.restore = false
  }
}

async function purgeExpired () {
  err.value = ''
  loading.purge = true
  try {
    await api.post('/ops/trash/purge', { })
    await loadTrash()
    await loadStorage()
  } catch (e) {
    setError(e)
  } finally {
    loading.purge = false
  }
}

async function purgeAll () {
  if (!confirm('This will permanently delete ALL trash contents. Continue?')) return
  err.value = ''
  loading.purge = true
  try {
    await api.post('/ops/trash/purge', { purge_all: true })
    await loadTrash()
    await loadStorage()
  } catch (e) {
    setError(e)
  } finally {
    loading.purge = false
  }
}

async function purgePath (path) {
  if (!confirm('Permanently delete this trash entry?')) return
  err.value = ''
  loading.purge = true
  try {
    await api.post('/ops/trash/purge', { path })
    await loadTrash()
    await loadStorage()
  } catch (e) {
    setError(e)
  } finally {
    loading.purge = false
  }
}

async function runExport () {
  if (!confirm('Export copies files on the server to the destination path. Continue?')) return
  err.value = ''
  loading.export = true
  try {
    lastExport.value = await api.post('/ops/export', exportReq).then(r => r.data)
  } catch (e) {
    setError(e)
  } finally {
    loading.export = false
  }
}

onMounted(async () => {
  user.value = getUser()
  if (isAdmin.value) {
    await loadStorage()
    await loadTrash()
  }
})
</script>
