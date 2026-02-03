import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './pages/HomePage.vue'
import CasePage from './pages/CasePage.vue'
import ViewerPage from './pages/ViewerPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/cases/:id', component: CasePage, props: true },
    { path: '/viewer', component: ViewerPage }
  ]
})
