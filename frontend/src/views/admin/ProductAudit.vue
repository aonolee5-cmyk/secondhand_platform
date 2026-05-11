<template>
  <div class="audit-container">
    <el-tabs v-model="activeTab" @tab-change="loadProducts">
      <el-tab-pane label="待初审商品" name="audit" />
      <el-tab-pane label="被举报商品" name="reported" /> <!-- 🚀 新增维度 -->
    </el-tabs>

    <el-table :data="products" style="width: 100%">
      <!-- 🚀 核心设计：展开行展示举报详情 -->
      <el-table-column type="expand">
        <template #default="props">
          <div class="report-detail-box">
            <h4 v-if="props.row.reports.length">举报详情：</h4>
            <el-timeline v-if="props.row.reports.length">
              <el-timeline-item
                v-for="(rep, index) in props.row.reports"
                :key="index"
                :timestamp="formatDate(rep.create_time)"
                :type="rep.status === 1 ? 'info' : 'danger'"
              >
                <p><strong>举报人：</strong>{{ rep.reporter_name }}</p>
                <p><strong>原因：</strong>{{ rep.reason }}</p>
                <p><strong>具体内容：</strong>{{ rep.content }}</p>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无被举报记录" :image-size="60" />
          </div>
        </template>
      </el-table-column>

      <el-table-column label="预览" width="80">
        <template #default="scope">
          <el-image :src="resolveImageUrl(scope.row.images[0])" class="mini-img" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="商品标题" />
      <el-table-column prop="owner_name" label="卖家" width="120" />
      <el-table-column prop="price" label="预售价" width="100" />
      
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button-group>
            <el-button type="success" size="small" @click="handleAction(scope.row.id, 'onsale')">通过/上架</el-button>
            <el-button type="danger" size="small" @click="handleAction(scope.row.id, 'off')">封禁/下架</el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const activeTab = ref('audit')
const products = ref([])

const loadProducts = async () => {
  // 如果是“被举报商品”页，逻辑可以改为：请求所有含有 report 的商品
  // 这里简化处理：依然请求列表，后端逻辑会根据状态返回
  const res = await request({ 
    url: '/goods/list/', 
    method: 'get', 
    params: { status: activeTab.value === 'reported' ? 'onsale' : activeTab.value, mine: 0 }
  })
  
  let data = res.results || res
  // 如果是显示被举报的，前端过滤一下有 reports 的数据
  if (activeTab.value === 'reported') {
    data = data.filter(item => item.reports && item.reports.length > 0)
  }
  products.value = data
}

const handleAction = async (id, status) => {
  await request({ 
    url: `/goods/list/${id}/change_status/`, 
    method: 'post', 
    data: { status: status } 
  })
  ElMessage.success('处理完成')
  loadProducts()
}

const resolveImageUrl = (url) => url ? 'http://127.0.0.1:8000' + url : ''
const formatDate = (d) => new Date(d).toLocaleString()

onMounted(loadProducts)
</script>

<style scoped>
.report-detail-box { padding: 20px 50px; background: #fafafa; }
.mini-img { width: 40px; height: 40px; border-radius: 4px; }
</style>