<template>
  <div class="sensitive-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="left">
            <el-icon><Lock /></el-icon>
            <span class="title">敏感词库管理</span>
          </div>
          <div class="right">
            <el-input
              v-model="searchQuery"
              placeholder="搜索词条..."
              class="search-input"
              @clear="fetchWords"
              clearable
            >
              <template #append>
                <el-button :icon="Search" @click="fetchWords" />
              </template>
            </el-input>
            <el-button type="primary" :icon="Plus" @click="handleAdd">新增词条</el-button>
          </div>
        </div>
      </template>

      <!-- 敏感词列表 -->
      <el-table :data="words" v-loading="loading" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="word" label="敏感词内容">
          <template #default="scope">
            <el-tag type="danger" effect="plain">{{ scope.row.word }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="添加时间" sortable>
          <template #default="scope">
            {{ new Date(scope.row.create_time).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-popconfirm title="确定要删除这个词条吗？" @confirm="handleDelete(scope.row.id)">
              <template #reference>
                <el-button type="danger" link :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增对话框 -->
    <el-dialog v-model="dialogVisible" title="新增敏感词" width="400px">
      <el-form :model="form" @submit.prevent="submitAdd">
        <el-form-item label="关键词">
          <el-input v-model="form.word" placeholder="请输入要拦截的违禁词" />
        </el-form-item>
        <p class="tip">提示：添加后，用户发布的商品标题和描述中若包含此词将无法发布。</p>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd" :loading="submitting">确定添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Delete, Lock } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const words = ref([])
const loading = ref(false)
const searchQuery = ref('')
const dialogVisible = ref(false)
const submitting = ref(false)
const form = reactive({ word: '' })

// 获取数据
const fetchWords = async () => {
  loading.value = true
  try {
    const res = await request({ 
      url: '/goods/admin/sensitive/', 
      method: 'get',
      params: { search: searchQuery.value }
    })
    words.value = res.results || res
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  form.word = ''
  dialogVisible.value = true
}

const submitAdd = async () => {
  if (!form.word.trim()) return ElMessage.warning('内容不能为空')
  submitting.value = true
  try {
    await request({ url: '/goods/admin/sensitive/', method: 'post', data: form })
    ElMessage.success('词条已加入库')
    dialogVisible.value = false
    fetchWords()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  await request({ url: `/goods/admin/sensitive/${id}/`, method: 'delete' })
  ElMessage.success('删除成功')
  fetchWords()
}

onMounted(fetchWords)
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  .left {
    display: flex;
    align-items: center;
    gap: 8px;
    .title { font-weight: bold; font-size: 16px; }
  }
  .right {
    display: flex;
    gap: 12px;
    .search-input { width: 250px; }
  }
}
.tip { font-size: 12px; color: #999; margin-top: 10px; }
</style>