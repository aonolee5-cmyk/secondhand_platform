<template>
  <div class="my-products">
    <el-page-header @back="$router.go(-1)" content="我发布的商品" />
    
    <el-table :data="myProducts" style="width: 100%; margin-top: 20px">
      <el-table-column label="图片" width="120">
        <template #default="scope">
          <el-image :src="'http://127.0.0.1:8000' + scope.row.images[0]" style="width: 80px; height: 80px" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="price" label="价格" width="100" />
      <el-table-column label="状态" width="120">
        <template #default="scope">
          <el-tag :type="statusMap[scope.row.status].type">
            {{ statusMap[scope.row.status].text }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" type="danger" v-if="scope.row.status === 'onsale'" @click="handleStatus(scope.row, 'off')">下架</el-button>
          <el-button size="small" type="success" v-if="scope.row.status === 'off'" @click="handleStatus(scope.row, 'onsale')">重新上架</el-button>
          <el-button size="small">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyProducts, updateProductStatus } from '@/api/goods'
import { ElMessage } from 'element-plus'

const myProducts = ref([])
const statusMap = {
  'audit': { text: '审核中', type: 'info' },
  'onsale': { text: '在售中', type: 'success' },
  'sold': { text: '已售出', type: 'warning' },
  'off': { text: '已下架', type: 'danger' }
}

const loadMyData = async () => {
  const res = await getMyProducts()
  myProducts.value = Array.isArray(res) ? res : (res.results || [])
}

const handleStatus = async (row, status) => {
  await updateProductStatus(row.id, status)
  ElMessage.success('操作成功')
  loadMyData()
}
onMounted(loadMyData)
</script>