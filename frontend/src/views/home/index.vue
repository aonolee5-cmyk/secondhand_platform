<template>
  <div class="home-container">
    <h1>二手物品交易平台 - 前端初始化成功</h1>
    <el-button type="primary" size="large" :icon="Edit">
      点我测试 Element Plus
    </el-button>
    <div class="card-area">
      <el-card shadow="hover">
        <template #header>项目状态</template>
        <p>Vue 3: <el-tag type="success">Ready</el-tag></p>
        <p>Vite: <el-tag type="success">Ready</el-tag></p>
        <p>Element Plus: <el-tag type="success">Ready</el-tag></p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { Edit } from '@element-plus/icons-vue'
// 不需要 import ElButton，插件会自动处理
</script>

<style scoped lang="scss">
.home-container {
  padding: 20px;
  text-align: center;
  
  h1 {
    color: #409EFF; // Element 主题色
    margin-bottom: 20px;
  }
  
  .card-area {
    margin-top: 30px;
    width: 400px;
    margin-left: auto;
    margin-right: auto;
  }
}
</style>