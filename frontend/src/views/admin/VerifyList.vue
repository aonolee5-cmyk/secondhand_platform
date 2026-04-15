<template>
  <div class="verify-list-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>实名信息审核</span>
          <el-radio-group v-model="statusFilter" size="small" @change="fetchData">
            <el-radio-button value="1">待审核</el-radio-button>
            <el-radio-button value="2">已通过</el-radio-button>
            <el-radio-button value="3">已驳回</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="verifyList" v-loading="loading" stripe>
        <el-table-column prop="username" label="申请账号" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="id_card" label="身份证号" />
        <el-table-column label="提交时间" width="180">
          <template #default="scope">{{ formatDate(scope.row.date_joined) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <div v-if="scope.row.verify_status === 1">
              <el-button type="success" size="small" @click="handleVerify(scope.row, 2)">通过</el-button>
              <el-button type="danger" size="small" @click="handleVerify(scope.row, 3)">驳回</el-button>
            </div>
            <el-tag v-else :type="scope.row.verify_status === 2 ? 'success' : 'danger'">
              已处理
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const verifyList = ref([])
const statusFilter = ref('1') // 默认看待审核

const fetchData = async () => {
  loading.value = true
  try {
    // 🚀 这里调用之前写的管理接口，带上过滤参数
    const res = await request({ 
      url: '/users/admin/users/', 
      method: 'get',
      params: { verify_status: statusFilter.value }
    })
    verifyList.value = res.results || res
  } finally {
    loading.value = false
  }
}

const handleVerify = async (row, targetStatus) => {
  try {
    // 🚀 调用后端更新接口（复用之前 UserViewSet 的逻辑或新建专用逻辑）
    await request({ 
      url: `/users/admin/users/${row.id}/`, 
      method: 'patch', 
      data: { verify_status: targetStatus, is_verified: targetStatus === 2 } 
    })
    ElMessage.success('操作成功')
    fetchData() // 刷新列表
  } catch (err) {
    console.error(err)
  }
}

const formatDate = (d) => new Date(d).toLocaleString()
onMounted(fetchData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>