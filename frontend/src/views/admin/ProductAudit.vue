<template>
  <el-tabs v-model="activeTab" @tab-change="loadProducts">
    <el-tab-pane label="待审核" name="audit" />
    <el-tab-pane label="已发布" name="onsale" />
    <el-tab-pane label="已下架/违规" name="off" />
  </el-tabs>

  <el-table :data="products" stripe>
    <el-table-column label="预览" width="100">
      <template #default="scope">
        <el-image :src="'http://127.0.0.1:8000'+scope.row.images[0]" class="audit-img" />
      </template>
    </el-table-column>
    <el-table-column prop="title" label="商品描述" />
    <el-table-column prop="price" label="价格" width="100" />
    <el-table-column prop="owner_name" label="发布人" width="120" />
    <el-table-column label="操作">
      <template #default="scope">
        <div v-if="scope.row.status === 'audit'">
          <el-button type="success" size="small" @click="doAudit(scope.row.id, true)">准予上架</el-button>
          <el-button type="danger" size="small" @click="doAudit(scope.row.id, false)">驳回</el-button>
        </div>
        <el-button v-else type="danger" size="small" plain @click="doAudit(scope.row.id, false)">强制下架</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const activeTab = ref('audit')
const products = ref([])

const loadProducts = async () => {
  const res = await request({ 
    url: '/goods/list/', 
    method: 'get', 
    params: { status: activeTab.value, mine: 0 } // 获取全平台指定状态商品
  })
  products.value = res.results || res
}

const doAudit = async (id, isPass) => {
  await request({ 
    url: `/goods/list/${id}/change_status/`, 
    method: 'post', 
    data: { status: isPass ? 'onsale' : 'off' } 
  })
  ElMessage.success('审核处理成功')
  loadProducts()
}

onMounted(loadProducts)
</script>
<style scoped>.audit-img { width: 50px; height: 50px; border-radius: 4px; }</style>