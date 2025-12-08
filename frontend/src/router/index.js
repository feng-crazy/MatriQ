import { createRouter, createWebHistory } from 'vue-router'
import PipelineList from '@/views/PipelineList.vue'
import PipelineNew from '@/views/PipelineNew.vue'
import PipelineDetail from '@/views/PipelineDetail.vue'

const routes = [
  {
    path: '/',
    redirect: '/pipelines',
  },
  {
    path: '/pipelines',
    name: 'PipelineList',
    component: PipelineList,
  },
  {
    path: '/pipelines/new',
    name: 'PipelineNew',
    component: PipelineNew,
  },
  {
    path: '/pipelines/:id',
    name: 'PipelineDetail',
    component: PipelineDetail,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

