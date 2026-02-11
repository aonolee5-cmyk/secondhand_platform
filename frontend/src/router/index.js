import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 首页
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/home/index.vue')
  },
  // 登录页面
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/login.vue')
  },
  // 注册页面
  {
  path:'/register',
  name:'Register',
  component: () => import('@/views/auth/register.vue')
  },
  // 发布商品页面
  {
    path: '/post',
    name: 'Post',
    component: () => import('@/views/goods/Post.vue'),
    meta: { requireAuth: true } // 只有登录才能发布
  },
// 我的商品页面
  {
    path: '/my-products',
    name: 'MyProducts',
    component: () => import('@/views/user/MyProducts.vue'),
  },
  // 个人中心
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { requireAuth: true } // 只有登录才能访问,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router