<template>
  <div class="history-container">
    <el-card shadow="never">
      <template #header>
        <div class="header">
          <span>我的足迹 ({{ historyList.length }})</span>
          <div class="btns">
            <el-button type="danger" plain size="small" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="danger" size="small" @click="handleClearAll">清空所有</el-button>
          </div>
        </div>
      </template>

      <el-table :data="historyList" @selection-change="handleSelectionChange" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column label="商品信息">
          <template #default="scope">
            <div class="prod-item" @click="$router.push('/product/'+scope.row.product)">
              <el-image :src="'http://127.0.0.1:8000'+scope.row.product_image" class="thumb" />
              <div class="info">
                <p class="title">{{ scope.row.product_title }}</p>
                <p class="time">浏览于：{{ formatDate(scope.row.viewed_time) }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="product_price" label="价格" width="120" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="danger" link @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const historyList = ref([])
const selectedIds = ref([])

const loadHistory = async () => {
  loading.value = true
  const res = await request({ url: '/goods/history/', method: 'get' })
  historyList.value = res.results || res
  loading.value = false
}

const handleSelectionChange = (val) => {
  selectedIds.value = val.map(i => i.id)
}

const handleDelete = async (id) => {
  await request({ url: `/goods/history/${id}/`, method: 'delete' })
  ElMessage.success('已删除')
  loadHistory()
}

const handleBatchDelete = async () => {
  // 批量删除逻辑：循环调用或后端写个批量接口
  for (let id of selectedIds.value) {
    await request({ url: `/goods/history/${id}/`, method: 'delete' })
  }
  ElMessage.success('批量删除成功')
  loadHistory()
}

const handleClearAll = async () => {
  await ElMessageBox.confirm('确定要清空所有浏览足迹吗？', '警告', { type: 'warning' })
  await request({ url: '/goods/history/clear_all/', method: 'post' })
  ElMessage.success('足迹已清空')
  loadHistory()
}

const formatDate = (d) => new Date(d).toLocaleString()
onMounted(loadHistory)
</script>

<style scoped lang="scss">
.prod-item { display: flex; align-items: center; cursor: pointer;
  .thumb { width: 60px; height: 60px; border-radius: 4px; margin-right: 15px; }
  .title { font-weight: bold; margin: 0; }
  .time { font-size: 12px; color: #999; margin: 5px 0 0; }
}
.header { display: flex; justify-content: space-between; align-items: center; }
</style>