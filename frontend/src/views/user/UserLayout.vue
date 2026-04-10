<template>
  <div class="user-center-container">
    <el-container class="main-content">
      <!-- 左侧菜单栏 -->
      <el-aside width="220px" class="user-aside">
        <el-menu
          :default-active="$route.path"
          router
          class="user-menu"
        >
          <el-menu-item index="/user/profile">
            <el-icon><User /></el-icon><span>个人中心</span>
          </el-menu-item>

          <el-sub-menu index="trade">
            <template #title>
              <el-icon><Goods /></el-icon><span>我的交易</span>
            </template>
            <el-menu-item index="/user/products">我发布的</el-menu-item>
            <el-menu-item index="/user/sell-orders">我卖出的</el-menu-item>
            <el-menu-item index="/user/orders">我买到的</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/user/favorites">
            <el-icon><Star /></el-icon><span>我的收藏</span>
          </el-menu-item>

          <el-sub-menu index="settings">
            <template #title>
              <el-icon><Setting /></el-icon><span>账户设置</span>
            </template>
            <el-menu-item index="/user/profile">个人资料</el-menu-item>
            <el-menu-item index="/user/security">账号与安全</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-main class="user-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<style scoped lang="scss">
.user-center-container {
  max-width: 1200px;
  margin: 20px auto;
  min-height: 80vh;
}
.user-aside {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  margin-right: 20px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  .user-menu { border-right: none; }
}
.user-main {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  padding: 0; // 内部由具体页面填充
}
</style>