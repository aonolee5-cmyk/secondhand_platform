<template>
  <div class="category-management">
    <el-card shadow="never" class="admin-card">
      <template #header>
        <div class="card-header">
          <div class="left">
            <el-icon><Menu /></el-icon>
            <span class="title">商品分类与属性管理</span>
          </div>
          <div class="right">
            <el-input
              v-model="searchQuery"
              placeholder="搜索分类名称..."
              class="search-input"
              clearable
              @clear="fetchCategories"
            >
              <template #append>
                <el-button :icon="Search" @click="fetchCategories" />
              </template>
            </el-input>
            <el-button type="primary" :icon="Plus" @click="handleAddCategory">新增分类</el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="categories" v-loading="loading" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="80" align="center" />
        
        <el-table-column prop="name" label="分类名称" width="150" />
        
        <el-table-column label="扩展属性">
          <template #default="scope">
            <div class="tag-container">
              <!-- 属性标签 -->
              <el-tag
                v-for="field in scope.row.attribute_fields"
                :key="field"
                closable
                type="success"
                effect="plain"
                class="field-tag"
                @close="handleRemoveField(scope.row, field)"
              >
                {{ field }}
              </el-tag>
              
              <!-- 快速新增标签按钮 -->
              <el-input
                v-if="scope.row.fieldInputVisible"
                :ref="el => setInputRef(el, scope.row.id)"
                v-model="scope.row.fieldInputValue"
                class="new-field-input"
                size="small"
                @keyup.enter="handleAddField(scope.row)"
                @blur="handleAddField(scope.row)"
              />
              <el-button v-else size="small" class="add-tag-btn" @click="showFieldInput(scope) ">
                + 新增属性
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center">
          <template #default="scope">
            <el-button type="primary" link @click="handleEditName(scope.row)">修改名称</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>


    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="400px">
      <el-form :model="categoryForm" label-position="top">
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称，如：数码产品" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCategory">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Search, Plus, Menu } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const categories = ref([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('')
const categoryForm = reactive({ id: null, name: '' })
const inputRefs = {}

const setInputRef = (el, id) => { if (el) inputRefs[id] = el }

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await request({ url: '/goods/admin/categories/', method: 'get', params: { search: searchQuery.value } })
    categories.value = res.results ? res.results.map(item => ({
      ...item,
      fieldInputVisible: false,
      fieldInputValue: ''
    })) : res.map(item => ({
      ...item,
      fieldInputVisible: false,
      fieldInputValue: ''
    }))
  } finally {
    loading.value = false
  }
}

// 分类增改逻辑
const handleAddCategory = () => {
  dialogTitle.value = '新增商品分类'
  categoryForm.id = null
  categoryForm.name = ''
  dialogVisible.value = true
}

const handleEditName = (row) => {
  dialogTitle.value = '修改分类名称'
  categoryForm.id = row.id
  categoryForm.name = row.name
  dialogVisible.value = true
}

const submitCategory = async () => {
  if (!categoryForm.name) return ElMessage.warning('请输入名称')
  const method = categoryForm.id ? 'patch' : 'post'
  const url = categoryForm.id ? `/goods/admin/categories/${categoryForm.id}/` : '/goods/admin/categories/'
  
  await request({ url, method, data: { name: categoryForm.name } })
  ElMessage.success('操作成功')
  dialogVisible.value = false
  fetchCategories()
}

// 动态属性增删
const showFieldInput = (scope) => {
  scope.row.fieldInputVisible = true
  nextTick(() => {
    inputRefs[scope.row.id]?.focus()
  })
}

const handleAddField = async (row) => {
  const val = row.fieldInputValue.trim()
  if (val) {
    if (row.attribute_fields.includes(val)) {
      ElMessage.warning('该属性已存在')
    } else {
      const updatedFields = [...row.attribute_fields, val]
      await syncFields(row.id, updatedFields)
      row.attribute_fields = updatedFields
    }
  }
  row.fieldInputVisible = false
  row.fieldInputValue = ''
}

const handleRemoveField = async (row, tag) => {
  const updatedFields = row.attribute_fields.filter(f => f !== tag)
  await syncFields(row.id, updatedFields)
  row.attribute_fields = updatedFields
}

const syncFields = async (id, fields) => {
  await request({
    url: `/goods/admin/categories/${id}/`,
    method: 'patch',
    data: { attribute_fields: fields }
  })
  ElMessage.success('模板同步成功')
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除分类 "${row.name}" 吗？这可能影响已关联的商品。`, '警告', { type: 'error' })
    .then(async () => {
      await request({ url: `/goods/admin/categories/${row.id}/`, method: 'delete' })
      ElMessage.success('删除成功')
      fetchCategories()
    })
}

onMounted(fetchCategories)
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  .left { display: flex; align-items: center; gap: 10px; .title { font-weight: bold; color: #333; } }
  .right { display: flex; gap: 15px; .search-input { width: 280px; } }
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  .field-tag { border-radius: 4px; }
  .new-field-input { width: 100px; }
  .add-tag-btn { border-style: dashed; }
}
</style>