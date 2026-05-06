<template>
  <div class="admin-wrapper">
    <el-container class="admin-container">
      <!-- 1. 侧边栏 -->
      <el-aside width="240px" class="admin-aside">
        <div class="admin-logo">
          <el-icon><Monitor /></el-icon>
          <span>{{ isSuper ? '系统管理中心' : '运营业务后台' }}</span>
        </div>
        

        <el-menu
          router
          :default-active="$route.path"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          class="admin-menu"
        >
          <div v-for="item in filteredMenu" :key="item.title">
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


            <el-menu-item v-else :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </div>
        </el-menu>
      </el-aside>

      <el-container class="main-content-area">
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

        <!-- 后台主体 -->
        <el-main class="admin-main">
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
import { ref, computed, onMounted, watch } from 'vue' 
import { useRoute } from 'vue-router' 
import { 
  Monitor, DataBoard, Goods, User, List, 
  Setting, Key, Operation, Connection, Checked 
} from '@element-plus/icons-vue'

const route = useRoute()


const username = ref('管理员')
const isSuper = ref(false)


const initAdminStatus = () => {
  const storedName = localStorage.getItem('username')
  const superStatus = localStorage.getItem('is_superuser') === 'true'
  
  username.value = storedName || '管理员'
  isSuper.value = superStatus
  
  // console.log(`[后台权限刷新] 当前用户: ${username.value}, 是否超级管理员: ${isSuper.value}`)
}


watch(() => route.path, () => {
  initAdminStatus()
}, { immediate: true }) 


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
      { title: '商品分类与属性管理', path: '/admin/categories' }
    ]
  }
]


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