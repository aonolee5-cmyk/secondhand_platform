import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/home/index.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/login.vue')
  },
  // 【新增：发布商品页面】
  {
    path: '/post',
    name: 'Post',
    component: () => import('@/views/goods/Post.vue'),
    meta: { requireAuth: true } // 只有登录才能发布
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router