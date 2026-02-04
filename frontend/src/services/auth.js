import { api } from './api'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'auth_user'

export function getToken () {
  return localStorage.getItem(TOKEN_KEY)
}

export function getUser () {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function setAuth (token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  api.defaults.headers.common.Authorization = `Bearer ${token}`
}

export function clearAuth () {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  delete api.defaults.headers.common.Authorization
}

export async function login (username, password) {
  const data = await api.post('/auth/login', { username, password }).then(r => r.data)
  setAuth(data.access_token, data.user)
  return data
}

export async function fetchMe () {
  const me = await api.get('/auth/me').then(r => r.data)
  localStorage.setItem(USER_KEY, JSON.stringify(me))
  return me
}

export function initAuth () {
  const token = getToken()
  if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`
}
