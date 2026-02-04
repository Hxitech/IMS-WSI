import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './pages/HomePage.vue'
import CasePage from './pages/CasePage.vue'
import ViewerPage from './pages/ViewerPage.vue'
import SlideViewerPage from './pages/SlideViewerPage.vue'
import LoginPage from './pages/LoginPage.vue'
import TaskCenterPage from './pages/TaskCenterPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginPage },
    { path: '/task-center', component: TaskCenterPage },
    { path: '/', component: HomePage },
    { path: '/cases/:id', component: CasePage, props: true },
    { path: '/viewer', component: ViewerPage },
    { path: '/slides/:slideId/view', component: SlideViewerPage, props: true }
  ]
})
