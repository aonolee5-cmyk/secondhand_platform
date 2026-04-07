<!-- frontend/src/views/admin/AdminLayout.vue -->
<template>
  <div class="admin-layout">
    <el-container style="height: 100vh">
      <!-- 侧边栏 -->
      <el-aside width="240px" class="aside">
        <div class="admin-logo">运营管理系统</div>
        <el-menu
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          :default-active="$route.path"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>数据大盘</span>
          </el-menu-item>
          <el-menu-item index="/admin/orders">
            <el-icon><List /></el-icon>
            <span>订单管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="admin-header">
          <div class="breadcrumb">运营中心 / {{ $route.meta.title }}</div>
          <el-button @click="$router.push('/')">回前台</el-button>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.aside { background-color: #304156; color: #fff; }
.admin-logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; font-weight: bold; background: #2b2f3a; }
.admin-header { background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
</style>