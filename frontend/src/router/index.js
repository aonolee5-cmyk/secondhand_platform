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
  // 商品详情页面
  {
    path: '/goods/:id',
    name: 'ProductDetail',
    component: () => import('@/views/goods/Detail.vue'),
  },
  // 修改商品页面
  {
    path: '/edit/:id',
    name: 'EditProduct',
    component: () => import('@/views/goods/Post.vue'),
    meta: { requireAuth: true } // 只有登录才能访问,
  },
  // 订单页面
  {
    path:'/orders',
    name:'Orders',
    component: () => import('@/views/trade/Orders.vue'),
    meta: { requireAuth: true } // 只有登录才能访问,
  },
  // 购物车页面
  {
    path:'/cart',
    name:'Cart',
    component: () => import('@/views/trade/Cart.vue'),
    meta: { requireAuth: true } // 只有登录才能访问,
  },
  // 聊天页面
  {
    path:'/chat/:targetId',
    name:'Chat',
    component: () => import('@/views/chat/Chat.vue'),
    meta: { requireAuth: true } // 只有登录才能访问,
  },
  // 聊天列表页面
  {
    path:'/chat-list',
    name:'ChatList',
    component: () => import('@/views/chat/List.vue'),
    meta: { requireAuth: true } // 只有登录才能访问,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router