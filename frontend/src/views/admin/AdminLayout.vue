<template>
  <div class="admin-wrapper">
    <el-container class="admin-container">
      <!-- 1. 侧边栏 -->
      <el-aside width="240px" class="admin-aside">
        <div class="admin-logo">
          <el-icon><Monitor /></el-icon>
          <span>{{ isSuper ? '系统管理中心' : '运营业务后台' }}</span>
        </div>
        
        <!-- 🚀 核心：动态渲染过滤后的菜单 -->
        <el-menu
          router
          :default-active="$route.path"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          class="admin-menu"
        >
          <div v-for="item in filteredMenu" :key="item.title">
            <!-- 情况A：有子菜单的（如商品治理） -->
            <el-sub-menu v-if="item.children" :index="item.index">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.title }}</span>
              </template>
              <el-menu-item 
                v-for="sub in item.children" 
                :key="sub.path" 
                :index="sub.path"
              >
                {{ sub.title }}
              </el-menu-item>
            </el-sub-menu>

            <!-- 情况B：普通菜单项（如控制台） -->
            <el-menu-item v-else :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </div>
        </el-menu>
      </el-aside>

      <el-container class="main-content-area">
        <!-- 2. 后台头部 -->
        <el-header class="admin-header">
          <div class="breadcrumb">
             <el-breadcrumb separator="/">
               <el-breadcrumb-item>运营中心</el-breadcrumb-item>
               <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
             </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-tag effect="dark" :type="isSuper ? 'danger' : 'success'" style="margin-right: 15px">
              {{ isSuper ? '超级管理员' : '运营客服' }}：{{ username }}
            </el-tag>
            <el-button type="primary" link icon="Back" @click="$router.push('/')">返回前台</el-button>
          </div>
        </el-header>

        <!-- 3. 后台主体 -->
        <el-main class="admin-main">
          <!-- 增加过渡动画，提升企业级质感 -->
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" :key="$route.fullPath"/>
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue' // 🚀 引入 watch
import { useRoute } from 'vue-router' // 🚀 引入 useRoute
import { 
  Monitor, DataBoard, Goods, User, List, 
  Setting, Key, Operation, Connection, Checked 
} from '@element-plus/icons-vue'

const route = useRoute()

// 1. 定义响应式变量
const username = ref('管理员')
const isSuper = ref(false)

// 2. 🚀 核心逻辑：定义一个统一的初始化函数
const initAdminStatus = () => {
  const storedName = localStorage.getItem('username')
  const superStatus = localStorage.getItem('is_superuser') === 'true'
  
  username.value = storedName || '管理员'
  isSuper.value = superStatus
  
  console.log(`[后台权限刷新] 当前用户: ${username.value}, 是否超级管理员: ${isSuper.value}`)
}

// 3. 🚀 关键修复：监听路由变化
// 只要路由发生变动（比如从首页跳到后台），就强行重新读取一次缓存
watch(() => route.path, () => {
  initAdminStatus()
}, { immediate: true }) // immediate 确保组件第一次加载时就跑一遍

// 定义全量菜单配置（保持你的配置结构不变）
const menuConfig = [
  { 
    title: '控制台大盘', 
    path: '/admin/dashboard', 
    icon: 'DataBoard', 
    role: 'all'
  },
  {
    title: '业务治理',
    index: 'ops',
    icon: 'Goods',
    role: 'staff_only', 
    children: [
      { title: '商品合规审核', path: '/admin/products' },
      { title: '订单纠纷仲裁', path: '/admin/orders' },
      { title: '实名认证审核', path: '/admin/verify' }
    ]
  },
  {
    title: '系统运维',
    index: 'sys',
    icon: 'Setting',
    role: 'admin_only', 
    children: [
      { title: '用户合规治理', path: '/admin/users' },
      { title: '敏感词维护', path: '/admin/sensitive' },
      { title: '商品类别管理', path: '/admin/categories' }
    ]
  }
]

// 根据身份过滤菜单（现在 isSuper 是响应式的，它变了，菜单会自动变）
const filteredMenu = computed(() => {
  return menuConfig.filter(item => {
    if (item.role === 'all') return true
    if (item.role === 'admin_only') return isSuper.value
    if (item.role === 'staff_only') return !isSuper.value
    return false
  })
})

onMounted(() => {
  initAdminStatus()
})
</script>

<style scoped lang="scss">
/* 保持你原有的 CSS 不变，只需增加一个动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}
.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* 其他你提供的 CSS 复制在这里... */
.admin-wrapper {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: #f0f2f5; z-index: 2000;
}
.admin-container { height: 100vh; }
.admin-aside {
  background-color: #304156; transition: width 0.3s; overflow-x: hidden;
  .admin-logo {
    height: 60px; display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: bold; font-size: 18px; background: #2b2f3a;
    span { margin-left: 10px; }
  }
  .admin-menu { border-right: none; }
}
.admin-header {
  background: #fff; height: 60px !important; display: flex;
  align-items: center; justify-content: space-between; padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}
.admin-main { padding: 20px; background-color: #f0f2f5; }
</style>