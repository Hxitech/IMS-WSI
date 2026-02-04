import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({ baseURL })

export const listCases = () => api.get('/cases').then(r => r.data)
export const createCase = (payload) => api.post('/cases', payload).then(r => r.data)
export const getCase = (id) => api.get(`/cases/${id}`).then(r => r.data)
export const listSlides = (caseId) => api.get(`/cases/${caseId}/slides`).then(r => r.data)
export const uploadSlide = (caseId, file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/cases/${caseId}/slides/upload`, form, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
}
export const listTasks = (caseId) => api.get(`/cases/${caseId}/tasks`).then(r => r.data)
export const createTask = (payload) => api.post('/tasks', payload).then(r => r.data)
export const updateTask = (taskId, payload) => api.patch(`/tasks/${taskId}`, payload).then(r => r.data)

export const fileUrl = (relPath) => `${baseURL}/files/${relPath}`



// Task Center
export const taskCenterTasks = () => api.get('/task-center/tasks').then(r => r.data)
export const taskCenterUsers = () => api.get('/task-center/users').then(r => r.data)
export const taskAssignManual = (taskId, assignee_id) => api.post(`/task-center/tasks/${taskId}/assign`, { assignee_id }).then(r => r.data)
export const taskAssignAuto = (taskId, payload) => api.post(`/task-center/tasks/${taskId}/auto-assign`, payload).then(r => r.data)
