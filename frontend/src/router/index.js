import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '@/views/admin/AdminLayout.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import AdminOrders from '@/views/admin/OrderList.vue'

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

  // 后台
  {
  path: '/admin',
  component: AdminLayout, 
  redirect: '/admin/dashboard',
  meta: { title: '管理中心', requiresAdmin: true },
  children: [
    {
      path: 'dashboard',
      name: 'AdminDashboard',
      component: () => import('@/views/admin/Dashboard.vue'), // 建议用懒加载
      meta: { title: '数据大盘' }
    },
    {
      path: 'orders',
      name: 'AdminOrders',
      component: () => import('@/views/admin/OrderList.vue'),
      meta: { title: '纠纷仲裁' }
    },
    // 【核心新增：对应侧边栏的商品管理】
    {
      path: 'products',
      name: 'AdminProducts',
      component: () => import('@/views/admin/ProductAudit.vue'),
      meta: { title: '商品审核' }
    },
    {
      path: 'sensitive',
      name: 'AdminSensitive',
      component: () => import('@/views/admin/SensitiveWords.vue'),
      meta: { title: '敏感词库' }
    },
    // 【核心新增：对应侧边栏的用户安全】
    {
      path: 'users',
      name: 'AdminUsers',
      component: () => import('@/views/admin/UserList.vue'),
      meta: { title: '用户管理' }
    }
  ]
}
]

const router = createRouter ({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isStaff = localStorage.getItem('is_staff') == 'true'
  if (to.path.startsWith('/admin') && !isStaff) {
    ElMessage.error('该区域仅限管理人员进入')
    next('/')
  } else {
    next()
  }
})



export default router