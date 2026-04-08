<template>
  <div class="admin-wrapper">
    <el-container class="admin-container">
      <!-- 1. 侧边栏：固定宽度，背景色加深 -->
      <el-aside width="240px" class="admin-aside">
        <div class="admin-logo">
          <el-icon><Monitor /></el-icon>
          <span>运营管理系统</span>
        </div>
        <el-menu
          router
          :default-active="$route.path"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          class="admin-menu"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataBoard /></el-icon><span>控制台大盘</span>
          </el-menu-item>
          
          <el-sub-menu index="goods">
            <template #title><el-icon><Goods /></el-icon><span>商品治理</span></template>
            <el-menu-item index="/admin/products">商品审核</el-menu-item>
            <el-menu-item index="/admin/sensitive">敏感词库</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="users">
            <template #title><el-icon><User /></el-icon><span>用户安全</span></template>
            <el-menu-item index="/admin/users">用户管理列表</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/admin/orders">
            <el-icon><List /></el-icon><span>订单仲裁中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container class="main-content-area">
        <!-- 2. 后台头部：白色背景，阴影效果 -->
        <el-header class="admin-header">
          <div class="breadcrumb">
             <el-breadcrumb separator="/">
               <el-breadcrumb-item>运营中心</el-breadcrumb-item>
               <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
             </el-breadcrumb>
          </div>
          <el-button type="primary" link icon="Back" @click="$router.push('/')">返回前台首页</el-button>
        </el-header>

        <!-- 3. 后台主体：浅灰色底色，让白色卡片浮出来 -->
        <el-main class="admin-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped lang="scss">
.admin-wrapper {
  // 核心：强行覆盖 App.vue 的淡紫色背景，确保后台环境纯净
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #f0f2f5; 
  z-index: 2000; // 确保盖在所有前台元素之上
}

.admin-container {
  height: 100vh;
}

.admin-aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow-x: hidden;
  
  .admin-logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: bold;
    font-size: 18px;
    background: #2b2f3a;
    span { margin-left: 10px; }
  }
  
  .admin-menu {
    border-right: none;
  }
}

.admin-header {
  background: #fff;
  height: 60px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.admin-main {
  padding: 20px;
  background-color: #f0f2f5; // 企业后台标准浅灰底
}
</style>