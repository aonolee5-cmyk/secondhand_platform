import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '@/views/admin/AdminLayout.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import AdminOrders from '@/views/admin/OrderList.vue'
import { ElMessage } from 'element-plus'
import UserLayout from '@/views/user/UserLayout.vue'
import Profile from '@/views/user/Profile.vue'
import orders from '@/views/trade/Orders.vue'


// 1. 定义路由
const routes = [
  // --- 公共页面 ---
  { path: '/', name: 'Home', component: () => import('@/views/home/index.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/auth/login.vue') },
  { path: '/register', name: 'Register', component: () => import('@/views/auth/register.vue') },
  { path: '/product/:id', name: 'ProductDetail', component: () => import('@/views/goods/Detail.vue') },

  // --- 核心业务（需要登录，但不需要侧边栏布局） ---
  { path: '/post', name: 'Post', component: () => import('@/views/goods/Post.vue'), meta: { auth: true } },
  { path: '/edit/:id', name: 'EditProduct', component: () => import('@/views/goods/Post.vue'), meta: { auth: true } },
  { path: '/cart', name: 'Cart', component: () => import('@/views/trade/Cart.vue'), meta: { auth: true } },
  { path: '/chat/:targetId', name: 'Chat', component: () => import('@/views/chat/Chat.vue'), meta: { auth: true } },
  { path: '/chat-list', name: 'ChatList', component: () => import('@/views/chat/List.vue'), meta: { auth: true } },

  {
    path: '/payment/:id',
    name: 'Payment',
    component: () => import('@/views/trade/Payment.vue'), // 检查文件路径是否正确
    meta: { title: '订单支付' }
  },
  {
    path: '/pay-success',
    name: 'PaySuccess',
    component: () => import('@/views/trade/PaySuccess.vue'),
    meta: { title: '支付成功' }
  },

  {
  path: '/order-detail/:id',
  name: 'OrderDetail',
  component: () => import('@/views/trade/OrderDetail.vue'),
  meta: { title: '订单详情' }
  },

  // --- 个人中心模块 (User Center) - 对应你图片二的布局 ---
  {
    path: '/user',
    component: () => import('@/views/user/UserLayout.vue'), // 侧边栏布局
    redirect: '/user/profile',
    meta: { auth: true },
    children: [
      { path: 'profile', name: 'UserProfile', component: () => import('@/views/user/Profile.vue'), meta: { title: '个人资料' } },
      { path: 'products', name: 'UserProducts', component: () => import('@/views/user/MyProducts.vue'), meta: { title: '我发布的' } },
      { path: 'orders', name: 'UserOrders', component: () => import('@/views/trade/Orders.vue'), meta: { title: '我的交易' } },
      { path: 'favorites', name: 'UserFavorites', component: () => import('@/views/user/Favorites.vue'), meta: { title: '我的收藏' } },
      { path: 'security', name: 'UserSecurity', component: () => import('@/views/user/Security.vue'), meta: { title: '账号安全' } },
      { path: 'sell-orders', name: 'UserSellOrders', component: () => import('@/views/trade/Orders.vue'), meta: { title: '我卖出的', defaultTab: 'sell' } },
    ]
  },

  // --- 后台管理模块 (Admin Dashboard) - 仅管理员可见 ---
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'), // 深色侧边栏布局
    redirect: '/admin/dashboard',
    meta: { auth: true, admin: true },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '数据大盘' } },
      { path: 'orders', name: 'AdminOrders', component: () => import('@/views/admin/OrderList.vue'), meta: { title: '纠纷仲裁' } },
      { path: 'products', name: 'AdminProducts', component: () => import('@/views/admin/ProductAudit.vue'), meta: { title: '商品审核' } },
      { path: 'sensitive', name: 'AdminSensitive', component: () => import('@/views/admin/SensitiveWords.vue'), meta: { title: '敏感词库' } },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/UserList.vue'), meta: { title: '用户管理' } },
      {
      path: 'verify', 
      name: 'AdminVerify',
      component: () => import('@/views/admin/VerifyList.vue'), 
      meta: { title: '实名认证审核' }
    },
    ]
  }
]
const router = createRouter ({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const username = localStorage.getItem('username')
  const isStaff = localStorage.getItem('is_staff') == 'true'
  const whiteList = ['Home', 'Login', 'Register', 'ProductDetail']
  if (whiteList.includes(to.name)){
    return next()
  }
  if (!token) {
    ElMessage.warning('请先登录后再访问该页面')
  }

  if (to.path.startsWith('/admin') && !isStaff) {
    ElMessage.error('该区域仅限管理人员进入')
    return next('/')
  } 
  next()
})



export default router