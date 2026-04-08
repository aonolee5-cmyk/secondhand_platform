<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">全平台用户合规治理</span>
      </div>
    </template>

    <el-table :data="users" style="width: 100%">
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="mobile" label="绑定手机" />
      <el-table-column label="实名状态">
        <template #default="scope">
          <el-tag :type="scope.row.is_verified ? 'success' : 'info'">
            {{ scope.row.is_verified ? '已实名' : '未认证' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="credit_score" label="信用分" sortable>
        <template #default="scope">
          <b :style="{ color: scope.row.credit_score < 60 ? '#F56C6C' : '#67C23A' }">
            {{ scope.row.credit_score }}
          </b>
        </template>
      </el-table-column>
      <el-table-column label="账号状态">
        <template #default="scope">
          <!-- 这里使用开关直接修改 is_active 字段 -->
          <el-switch
            v-model="scope.row.is_active"
            inline-prompt
            active-text="正常"
            inactive-text="封禁"
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="管理操作">
        <template #default="scope">
          <el-button type="primary" size="small" link @click="resetPwd(scope.row)">重置密码</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const users = ref([])

const loadUsers = async () => {
  const res = await request({ url: '/users/admin/users/', method: 'get' })
  users.value = res.results || res
}

const handleStatusChange = async (row) => {
  try {
    await request({ url: `/users/admin/users/${row.id}/toggle_status/`, method: 'post' })
    ElMessage.success(`用户 ${row.username} 状态已更新`)
  } catch (err) {
    row.is_active = !row.is_active // 失败则回滚 UI 状态
  }
}

onMounted(loadUsers)
</script>