<template>
  <div class="app-wrapper">
    <!-- 全局头部导航 -->
    <el-header class="main-header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon color="#409EFF" :size="28"><Shop /></el-icon>
          <span>二手交易平台</span>
        </div>

        <div class="search-bar">
          <el-input v-model="searchQuery" placeholder="搜宝贝、搜分类..." :prefix-icon="Search" clearable @keyup.enter="handleSearch"/>
          <el-button :icon="Search" @click="handleSearch">搜</el-button>
        </div>

        <div class="nav-actions">
          <el-button type="primary" plain :icon="Plus" @click="goToPost">发布闲置</el-button>
          
          <el-divider direction="vertical" />

          <!-- 根据是否登录显示不同内容 -->
          <div v-if="!isLogin" class="auth-btns">
            <el-button text @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" @click="$router.push('/register')">注册</el-button>
          </div>

          <div v-else class="user-profile">
            <el-dropdown>
              <span class="el-dropdown-link">
                <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人中心</el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/my-products')">我的发布</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </el-header>

    <!-- 页面内容出口 -->
    <el-main class="main-body">
      <router-view />
    </el-main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, Plus, Shop, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { el } from 'element-plus/es/locale/index.mjs'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const isLogin = ref(false)

// 检查登录状态
const checkLogin = () => {
  const token = localStorage.getItem('token')
  isLogin.value = !!token
}

// 监听路由变化，每次切页面都检查下登录（简单处理）
watch(() => route.path, () => {
  checkLogin()
})

const goToPost = () => {
  if (!isLogin.value) {
    ElMessage.warning('请先登录后再发布商品')
    router.push('/login')
    return
  }
  router.push('/post')
}

const handleLogout = () => {
  localStorage.removeItem('token')
  isLogin.value = false
  ElMessage.success('已安全退出')
  router.push('/')
}

// 处理搜索
const handleSearch = () => {
  if (!searchQuery.value) return
  // 跳转到首页，并带上搜索参数
  router.push({ path: '/', query: { q: searchQuery.value || undefined } })
}
</script>

<style lang="scss">
/* 这里就是 HTML 的外衣：CSS */
.app-wrapper {
  background-color: #f5f7fa;
  min-height: 100vh;
}

.main-header {
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 64px !important;

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .logo {
      display: flex;
      align-items: center;
      cursor: pointer;
      span {
        margin-left: 10px;
        font-size: 18px;
        font-weight: bold;
        color: #409EFF;
      }
    }

    .search-bar {
      flex: 1;
      max-width: 400px;
      margin: 0 40px;
    }

    .nav-actions {
      display: flex;
      align-items: center;
    }
  }
}

.main-body {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0;
}
</style>