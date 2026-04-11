<template>
  <div class="app-wrapper">
    <!-- 1. 企业级顶部导航栏：采用 1:2:1 比例分布 -->
    <el-header class="main-header">
      <div class="header-content">
        <!-- 左侧：Logo区 -->
        <div class="logo-section" @click="$router.push('/')">
          <div class="logo-icon">
            <el-icon><Shop /></el-icon>
          </div>
          <span class="logo-text"><span class="highlight">二手交易平台</span></span>
        </div>

        <!-- 中间：搜索区 (自适应宽度，带最大值限制) -->
        <div class="search-section" v-if="isSearchPage">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索你想要的宝贝..." 
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>

        <!-- 右侧：动作区 (靠右对齐) -->
        <div class="action-section">
          <el-button type="primary" :icon="Plus" class="post-btn" @click="goToPost" round>发布宝贝</el-button>
          
          <el-divider direction="vertical" />

          <div v-if="!isLogin" class="auth-box">
            <el-button text @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" plain @click="$router.push('/register')">注册</el-button>
          </div>

          <div v-else class="user-control">
            <!-- 消息提醒 -->
            <el-badge :value="unreadTotal" :hidden="unreadTotal === 0" class="badge-item">
              <el-button circle :icon="ChatLineRound" @click="$router.push('/chat-list')" />
            </el-badge>

            <!-- 购物车 -->
            <el-tooltip content="购物车" placement="bottom">
              <el-button circle :icon="ShoppingCart" @click="$router.push('/cart')" class="cart-btn" />
            </el-tooltip>

            <!-- 闲鱼级下拉卡片 -->
            <el-dropdown trigger="hover" placement="bottom-end">
              <div class="user-trigger" @click="handleCommand('/user/profile')">
                <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                <span class="user-name">{{ username }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>

              <template #dropdown>
                <div class="xianyu-profile-card">
                  <div class="card-header" @click="handleCommand('/user/profile')" style="cursor: pointer;">
                    <el-avatar :size="50" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                    <div class="header-info">
                      <div class="nickname">{{ username }}</div>
                      <div class="stats">
                      </div>
                    </div>
                  </div>

                  <div class="menu-rows">
                    <div class="menu-row" @click="handleCommand('/user/profile')">
                      <span class="row-title">个人主页</span>
                      <div class="row-right">
                        <span class="count" style="font-size: 12px; color: #409EFF;">去编辑</span>
                        <el-icon><ArrowRight /></el-icon>
                      </div>
                    </div>
                    <div class="menu-row" @click="handleCommand('/user/products')">
                      <span class="row-title">我卖出的</span>
                      <div class="row-right">
                        <span class="count">{{ userStats.sell_count }}</span>
                        <el-icon><ArrowRight /></el-icon>
                      </div>
                    </div>
                    <div class="menu-row" @click="handleCommand('/user/orders')">
                      <span class="row-title">我买到的</span>
                      <div class="row-right">
                        <span class="count">{{ userStats.buy_count }}</span>
                        <el-icon><ArrowRight /></el-icon>
                      </div>
                    </div>
                    <div class="menu-row" @click="handleCommand('/user/favorites')">
                      <span class="row-title">我的收藏</span>
                      <div class="row-right">
                        <span class="count">{{ userStats.fav_count }}</span>
                        <el-icon><ArrowRight /></el-icon>
                      </div>
                    </div>
                    <!-- 管理员入口 -->
                    <div v-if="isAdmin" class="menu-row admin-row" @click="handleCommand('/admin')">
                      <div class="row-left">
                        <el-icon color="#E6A23C"><Monitor /></el-icon>
                        <span class="row-title" style="margin-left: 8px">管理后台</span>
                      </div>
                      <el-icon><ArrowRight /></el-icon>
                    </div>
                  </div>

                  <div class="card-footer">
                    <div class="logout-btn" @click="handleCommand('logout')">退出登录</div>
                    <div class="save-info">
                      <span>保存登录信息</span>
                      <el-switch size="small" v-model="saveLogin" active-color="#409EFF" />
                    </div>
                  </div>
                </div>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </el-header>

    <!-- 2. 主体展示区：增加背景色区分 -->
    <el-main class="main-container">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- 3. 企业级简约页脚 -->
    <el-footer class="footer">
      <div class="footer-content">
        <p>©二手物品交易平台</p>
        <div class="footer-links">
          <span>关于我们</span>
          <el-divider direction="vertical" />
          <span>联系客服</span>
          <el-divider direction="vertical" />
          <span>服务条款</span>
        </div>
      </div>
    </el-footer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Search, Plus, Shop, ArrowDown, ShoppingCart, 
  ChatLineRound, Monitor, ArrowRight, SwitchButton 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const isLogin = ref(false)
const isAdmin = ref(false)
const unreadTotal = ref(0)
const username = ref('')
const saveLogin = ref(true)

// 身份同步逻辑
const updateGlobalStatus = () => {
  const token = localStorage.getItem('token')
  const storedName = localStorage.getItem('username')
  const isStaff = localStorage.getItem('is_staff') === 'true'

  isLogin.value = !!token
  username.value = storedName || ''
  
  if (isLogin.value && storedName) {
    const nameLower = storedName.toLowerCase().trim()
    isAdmin.value = (nameLower === 'admin' || nameLower === 'lee' || isStaff)
  } else {
    isAdmin.value = false
  }
}

// 检查未读信息
const checkUnread = async () => {
  if (!isLogin.value) return
  try {
    const res = await request({ url: 'chat/history/list_recent_contacts/', method: 'get' })
    unreadTotal.value = res.unread_total || 0
  } catch (err) { /* 静默 */ }
}


// 处理登出
const handleCommand = (command) => {
  if (command === 'logout') {
    localStorage.clear()
    isLogin.value = false
    isAdmin.value = false
    ElMessage.success('已安全退出')
    window.location.href = '/'
  } else {
    router.push(command)
  }
}


// 处理搜索
const handleSearch = () => {
  const q = searchQuery.value.trim()
  router.push({ path: '/', query: { q: q } })
}

const goToPost = () => {
  if (!isLogin.value) {
    ElMessage.warning('请先登录后再发布商品')
    router.push('/login')
    return
  }
  router.push('/post')
}

const isSearchPage = computed(() => {
  // 首页显示搜索
  return route.path === '/' || route.meta.showSearch === true
})

const userStats = reactive({
  buy_count: 0,
  sell_count: 0,
  fav_count: 0
})

// 修改获取用户信息的逻辑
const fetchUserInfo = async () => {
  if (!localStorage.getItem('token')) return
  try {
    const res = await request({ url: '/users/profile/', method: 'get' })
    // 将后端传来的统计数字赋值给响应式变量
    userStats.buy_count = res.buy_count
    userStats.sell_count = res.sell_count
    userStats.fav_count = res.fav_count
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  updateGlobalStatus()
  fetchUserInfo()
  checkUnread()
  setInterval(checkUnread, 30000)
})

watch(() => route.path, (newPath) => {
  updateGlobalStatus()
  if (isLogin.value) {
    fetchUserInfo()
  }
  
  if (newPath.startsWith('/admin') && !isAdmin.value) {
    ElMessage.error('权限不足')
    // router.push('/')
  }
}, { immediate: true })
</script>

<style lang="scss">
/* --- 全局重置：消除廉价感的基石 --- */
body {
  margin: 0;
  padding: 0;
  background-color: #f6f8fa; /* 稍微深一点的灰白，显得高级 */
  font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto;
}

.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* --- 导航栏：三段式 Flex 布局 --- */
.main-header {
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  height: 70px !important;
  position: sticky;
  top: 0;
  z-index: 1000;

  .header-content {
    max-width: 1300px;
    margin: 0 auto;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
  }
}

.logo-section {
  display: flex;
  align-items: center;
  cursor: pointer;
  width: 250px; /* 固定左侧宽度，防止搜索框晃动 */
  .logo-icon {
    width: 38px;
    height: 38px;
    background: #409EFF;
    color: #fff;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    box-shadow: 0 4px 10px rgba(64, 158, 255, 0.3);
  }
  .logo-text {
    margin-left: 12px;
    font-size: 22px;
    font-weight: 800;
    color: #2c3e50;
    .highlight { color: #409EFF; }
  }
}

.search-section {
  flex: 1;
  max-width: 500px;
  margin: 0 40px;
  .search-input :deep(.el-input-group__append) {
    background-color: #409EFF;
    color: white;
    border: none;
    padding: 0 25px;
    font-weight: bold;
    &:hover { background-color: #66b1ff; }
  }
}

.action-section {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  width: 380px; /* 固定右侧宽度 */
  gap: 15px;

  .post-btn { font-weight: bold; }
  
  .user-trigger {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 5px 12px;
    border-radius: 20px;
    transition: all 0.3s;
    background: #f8f9fa;
    &:hover { background: #f0f2f5; }
    .user-name { font-size: 14px; font-weight: 500; color: #606266; }
  }
}

/* --- 内容容器 --- */
.main-container {
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
  padding: 30px 20px;
}

/* --- 页面切换动效 --- */
.page-fade-enter-active, .page-fade-leave-active {
  transition: all 0.3s ease;
}
.page-fade-enter-from { opacity: 0; transform: translateY(15px); }
.page-fade-leave-to { opacity: 0; transform: translateY(-15px); }

/* --- 闲鱼风格下拉卡片 CSS (保持之前的高级样式) --- */
.xianyu-profile-card {
  width: 280px;
  padding: 20px;
  background: #fff;
  border-radius: 16px;
  .card-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
    .nickname { font-size: 18px; font-weight: 700; }
    .stats { font-size: 12px; color: #999; b { color: #333; } }
  }
  .menu-rows {
    .menu-row {
      display: flex; justify-content: space-between; align-items: center;
      padding: 12px 15px; margin: 5px 0; border-radius: 10px;
      background: #f9fafb; cursor: pointer; transition: 0.2s;
      &:hover { background: #f3f4f6; transform: translateX(5px); }
      &.admin-row { background: #fff9f0; color: #e6a23c; font-weight: bold; }
    }
  }
  .card-footer {
    margin-top: 20px; padding-top: 15px; border-top: 1px solid #f3f4f6;
    display: flex; justify-content: space-between; align-items: center;
    .logout-btn { color: #999; font-size: 14px; cursor: pointer; &:hover { color: #f56c6c; } }
    .save-info { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #bbb; }
  }
}

/* --- 页脚：去廉价感 --- */
.footer {
  background: #fff;
  border-top: 1px solid #ebedf0;
  padding: 40px 0;
  margin-top: auto;
  text-align: center;
  color: #909399;
  font-size: 14px;
  .footer-links { margin-top: 15px; span { cursor: pointer; &:hover { color: #409EFF; } } }
}

:deep(.el-dropdown__popper) {
  border: none !important; box-shadow: none !important; background: transparent !important;
  .el-scrollbar { background: transparent !important; }
  .el-dropdown-menu { background: transparent !important; padding: 0 !important; }
}
</style>