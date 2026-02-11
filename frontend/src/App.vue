<template>
  <div class="app-wrapper">
    <!-- 全局头部导航 -->
    <el-header class="main-header">
      <div class="header-content">
        <!-- 优化点1: Logo区域增加交互效果 -->
        <div class="logo" @click="$router.push('/')" title="返回首页">
          <el-icon color="#409EFF" :size="32"><Shop /></el-icon>
          <span class="logo-text">二手交易平台</span>
        </div>

        <!-- 优化点2: 搜索框样式优化 -->
        <div class="search-bar">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜宝贝、搜好物..." 
            :prefix-icon="Search" 
            clearable 
            @keyup.enter="handleSearch"
            size="large"
          />
          <!-- 优化点3: 将搜索按钮集成到输入框内 -->
          <el-button type="primary" :icon="Search" @click="handleSearch" class="search-btn">搜索</el-button>
        </div>

        <div class="nav-actions">
          <!-- 优化点4: 发布按钮更突出 -->
          <el-button type="primary" :icon="Plus" @click="goToPost" size="large" round>发布宝贝</el-button>
          
          <el-divider direction="vertical" />

          <!-- 优化点5: 登录/注册按钮视觉优化 -->
          <div v-if="!isLogin" class="auth-btns">
            <el-button text bg @click="$router.push('/login')">登录</el-button>
            <el-button text bg @click="$router.push('/register')">注册</el-button>
          </div>

          <div v-else class="user-profile">
            <!-- 优化点6: 用户头像下拉菜单交互优化 -->
            <el-dropdown trigger="click">
              <span class="el-dropdown-link user-avatar-container">
                <el-avatar :size="40" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                <span class="username">欢迎您</span>
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/profile')">个人中心</el-dropdown-item>
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
      <!-- 优化点7: 内容区域增加过渡效果 -->
      <router-view v-slot="{ Component }">
        <transition name="fade-transform" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- 优化点8: 增加全局页脚 -->
    <el-footer class="main-footer">
      <p>&copy; 2024 二手交易平台. All Rights Reserved.</p>
      <p>
        <a href="#">关于我们</a> | <a href="#">联系我们</a> | <a href="#">服务条款</a>
      </p>
    </el-footer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, Plus, Shop, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const isLogin = ref(false)

const checkLogin = () => {
  const token = localStorage.getItem('token')
  isLogin.value = !!token
}

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

const handleSearch = () => {
  if (!searchQuery.value) return
  router.push({ path: '/', query: { q: searchQuery.value} })
}
</script>

<style lang="scss">
/* --- 全局样式优化 --- */
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  
  /* === 新增渐变背景 === */
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); /* 紫色到蓝色的柔和渐变 */
  /* 备选方案1: 清新绿意 */
  // background: linear-gradient(to top, #c1dfc4 0%, #deecdd 100%);
  /* 备选方案2: 温暖日落 */
  // background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  /* background-color: #f5f7fa; (不再需要这一行了，因为 body 已经有了背景) */
  min-height: 100vh;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* --- Header 头部导航优化 --- */
.main-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 64px !important;
  padding: 0 20px; /* 增加左右内边距 */

  .header-content {
    max-width: 1280px; /* 适当加宽内容区 */
    margin: 0 auto;
    height: 100%;
    display: flex;
    align-items: center;

    .logo {
      display: flex;
      align-items: center;
      cursor: pointer;
      transition: opacity 0.3s;

      &:hover {
        opacity: 0.8;
      }
      
      .logo-text {
        margin-left: 12px;
        font-size: 22px;
        font-weight: 600;
        color: #303133;
        white-space: nowrap; /* 防止文字换行 */
      }
    }

    .search-bar {
      display: flex;
      flex-grow: 1; /* 使其填充更多空间 */
      max-width: 500px;
      margin: 0 50px;

      .el-input--large {
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
      }
      
      .search-btn {
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
        font-size: 16px;
      }
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 12px; /* 使用 gap 增加元素间距 */

      .el-divider--vertical {
        height: 2em;
        margin: 0 8px;
      }
      
      .auth-btns .el-button {
        font-size: 14px;
      }

      .user-profile {
        .user-avatar-container {
          display: flex;
          align-items: center;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 20px;
          transition: background-color 0.3s;

          &:hover {
            background-color: #f5f7fa;
          }

          .username {
            margin: 0 8px;
            font-size: 14px;
            color: #606266;
          }
        }
      }
    }
  }
}

/* --- Main 内容区域优化 --- */
.main-body {
  flex-grow: 1; /* 确保内容区能撑开，将页脚推到底部 */
  max-width: 1280px;
  width: 100%;
  margin: 24px auto; /* 增加上下外边距 */
  padding: 0 20px;
  box-sizing: border-box; /* 确保 padding 不会撑大宽度 */
}

/* --- 路由切换动画 --- */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s ease;
}
.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* --- Footer 页脚样式 --- */
.main-footer {
  background-color: #303133;
  color: #a5a7ab;
  text-align: center;
  padding: 20px 0;
  font-size: 14px;
  
  a {
    color: #e4e7ed;
    text-decoration: none;
    margin: 0 10px;
    transition: color 0.3s;
    &:hover {
      color: #409EFF;
    }
  }
}
</style>