<template>
  <div class="product-audit-wrapper">
    <el-tabs v-model="activeTab" @tab-change="loadProducts">
      <el-tab-pane label="待审核" name="audit" />
      <el-tab-pane label="已发布" name="onsale" />
      <el-tab-pane label="已下架/违规" name="off" />
    </el-tabs>
  
    <el-table :data="products" stripe v-loading="loading">
      <el-table-column label="预览" width="100">
        <template #default="scope">
          <el-image 
            v-if="scope.row.images && scope.row.images.length > 0"
            :src="resolveImageUrl(scope.row.images[0])" 
            class="audit-img" 
            fit="cover"
            preview-teleported
            :preview-src-list="scope.row.images.map(i => resolveImageUrl(i))"
          />
          <el-tag v-else type="info" size="small">无图</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="title" label="商品标题" show-overflow-tooltip />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="scope"><b style="color: #f56c6c">￥{{ scope.row.price }}</b></template>
      </el-table-column>
      <el-table-column prop="owner_name" label="发布人" width="120" />

      <el-table-column label="管理操作" width="250">
        <template #default="scope">
          <el-button type="primary" size="small" link @click="openDetail(scope.row)">
            查看详情
          </el-button>
          
          <el-divider direction="vertical" />

          <template v-if="scope.row.status === 'audit'">
            <el-button type="success" size="small" @click="doAudit(scope.row.id, true)">通过</el-button>
            <el-button type="danger" size="small" @click="doAudit(scope.row.id, false)">拒绝</el-button>
          </template>
          <el-button v-else-if="scope.row.status === 'onsale'" type="danger" size="small" plain @click="doAudit(scope.row.id, false)">
            强制下架
          </el-button>
          <el-tag v-else type="info" size="small">已处理</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog 
      v-model="detailVisible" 
      title="商品发布合规性审核" 
      width="750px" 
      destroy-on-close
      top="5vh"
    >
      <div v-if="currentRow" class="audit-panel">
        <!-- 1. 卖家与基本信息 -->
        <el-descriptions title="基础信息" :column="2" border size="small">
          <el-descriptions-item label="商品标题" :span="2">{{ currentRow.title }}</el-descriptions-item>
          <el-descriptions-item label="卖家账号">{{ currentRow.owner_name }}</el-descriptions-item>
          <el-descriptions-item label="卖家信用">
            <el-tag :type="currentRow.owner_credit >= 80 ? 'success' : 'danger'" size="small">
              {{ currentRow.owner_credit || 100 }} 分
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="所属分类">{{ currentRow.category_name }}</el-descriptions-item>
          <el-descriptions-item label="售价">￥{{ currentRow.price }}</el-descriptions-item>
        </el-descriptions>

        <!-- 2. 动态参数审计 (JSONB 字段展示) -->
        <div class="audit-section-title">规格参数</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item 
            v-for="(val, key) in currentRow.attributes" 
            :key="key" 
            :label="key"
          >
            {{ val }}
          </el-descriptions-item>
          <el-descriptions-item v-if="!Object.keys(currentRow.attributes || {}).length" label="提示" :span="2">
            该商品未填写扩展属性
          </el-descriptions-item>
        </el-descriptions>

        <!-- 3. 详细描述 -->
        <div class="audit-section-title">详细描述</div>
        <div class="desc-content-box">
          {{ currentRow.desc }}
        </div>

        <!-- 4. 图片资源审计 -->
        <div class="audit-section-title">图片资源 (共 {{ currentRow.images?.length }} 张)</div>
        <div class="image-gallery">
          <el-image 
            v-for="(img, index) in currentRow.images" 
            :key="index"
            :src="resolveImageUrl(img)" 
            class="gallery-item"
            fit="cover"
            :preview-src-list="currentRow.images.map(i => resolveImageUrl(i))"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭预览</el-button>
        <template v-if="currentRow && currentRow.status === 'audit'">
          <el-button type="danger" @click="handleAuditInDialog(false)">拒绝并驳回</el-button>
          <el-button type="success" @click="handleAuditInDialog(true)">允许上架</el-button>
        </template>
      </template>
    </el-dialog>
  </div>   
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const activeTab = ref('audit')
const products = ref([])
const loading = ref(false)

// 🚀 弹窗逻辑状态
const detailVisible = ref(false)
const currentRow = ref(null)

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await request({ 
      url: '/goods/list/', 
      method: 'get', 
      params: { status: activeTab.value, mine: 0 } 
    })
    products.value = res.results || res
  } finally {
    loading.value = false
  }
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

// 🚀 在弹窗中执行审核
const handleAuditInDialog = async (isPass) => {
  await doAudit(currentRow.value.id, isPass)
  detailVisible.value = false
}

// 🚀 打开详情弹窗
const openDetail = (row) => {
  currentRow.value = row
  detailVisible.value = true
}

const resolveImageUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return 'http://127.0.0.1:8000' + path;
}

onMounted(loadProducts)
</script>

<style scoped lang="scss">
.product-audit-wrapper {
  padding: 10px;
}
.audit-img {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  cursor: zoom-in;
}
.audit-panel {
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 10px;
}
.audit-section-title {
  margin: 20px 0 10px;
  font-weight: bold;
  color: #333;
  border-left: 4px solid #409eff;
  padding-left: 10px;
  font-size: 14px;
}
.desc-content-box {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 13px;
}
.image-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-bottom: 20px;
  .gallery-item {
    width: 140px;
    height: 140px;
    border-radius: 6px;
    border: 1px solid #eee;
    cursor: zoom-in;
  }
}
</style>