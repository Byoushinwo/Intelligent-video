import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import Layout from '@/layouts/index.vue';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/video/list' },
  {
    path: '/video',
    component: Layout,
    redirect: '/video/list',
    children: [
      { path: 'list', name: 'VideoList', component: () => import('@/views/video/list/index.vue') },
      { path: 'search', name: 'VideoSearch', component: () => import('@/views/video/search/index.vue') },
      { path: 'detail/:id', name: 'VideoDetail', component: () => import('@/views/video/detail/index.vue') },
    ]
  },
  // 404路由
  { path: '/:pathMatch(.*)*', redirect: '/video/list' }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;