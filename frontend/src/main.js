import { createApp } from 'vue'
import App from './App.vue'
import { initAuth } from './services/auth'
import router from './router'

initAuth()

createApp(App).use(router).mount('#app')
