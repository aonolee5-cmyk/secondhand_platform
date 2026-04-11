<template>
  <div class="admin-dashboard">
    <!-- 顶部数据卡片 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statsCards" :key="card.title">
        <el-card shadow="hover" class="stat-card">
          <div class="card-content">
            <div class="title">{{ card.title }}</div>
            <div class="value">{{ card.prefix }}{{ card.value }}</div>
            <div class="footer">较昨日 <span :class="card.trend > 0 ? 'up' : 'down'">{{ card.trend }}%</span></div>
          </div>
          <el-icon class="card-icon" :color="card.color"><component :is="card.icon" /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 25px">
      <el-col :span="16">
        <el-card header="近7日平台交易趋势">
          <div ref="lineChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card header="全平台品类分布">
          <div ref="pieChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待办任务：待审核商品列表 -->
    <el-card header="待审核商品列表" style="margin-top: 25px">
       <el-table :data="auditList" stripe>
         <el-table-column label="商品名称">
          <template #default="scope">
            <!-- 🚀 修正：传入整个 scope.row 对象 -->
            <el-link 
              type="primary" 
              :underline="false" 
              @click="openAuditPreview(scope.row)"
            >
              {{ scope.row.title }}
            </el-link>
          </template>
        </el-table-column>
         <el-table-column prop="owner_name" label="发布者" />
         <el-table-column prop="price" label="预售价" />
         <el-table-column label="操作">
           <template #default="scope">
             <el-button type="success" size="small" @click="handleAudit(scope.row.id, 'onsale')">通过</el-button>
             <el-button type="danger" size="small" @click="handleAudit(scope.row.id, 'off')">拒绝</el-button>
           </template>
         </el-table-column>
       </el-table>
    </el-card>

    <!-- 🚀 商品发布参数审计弹窗 -->
    <el-dialog 
      v-model="auditPreviewVisible" 
      title="商品发布原始参数审计" 
      width="750px"
      destroy-on-close
    >
      <div v-if="previewItem" class="audit-panel">
        <el-descriptions title="核心发布数据" :column="2" border>
          <el-descriptions-item label="商品标题" :span="2">{{ previewItem.title }}</el-descriptions-item>
          <el-descriptions-item label="预售价">
            <b style="color: #f56c6c">￥{{ previewItem.price }}</b>
          </el-descriptions-item>
          <el-descriptions-item label="所属分类">{{ previewItem.category_name || '未分类' }}</el-descriptions-item>
          <el-descriptions-item label="发布者">{{ previewItem.owner_name }}</el-descriptions-item>
          <el-descriptions-item label="发布时间">{{ previewItem.create_time }}</el-descriptions-item>
        </el-descriptions>

        <!-- 展示 JSONB 扩展参数 -->
        <el-descriptions title="扩展规格参数" :column="1" border style="margin-top: 20px">
          <el-descriptions-item 
            v-for="(val, key) in previewItem.attributes" 
            :key="key" 
            :label="key"
          >
            {{ val }}
          </el-descriptions-item>
          <el-descriptions-item v-if="!Object.keys(previewItem.attributes || {}).length" label="扩展信息">
            该商品无额外规格参数
          </el-descriptions-item>
        </el-descriptions>

        <div class="audit-section">
          <h4>详细描述：</h4>
          <div class="desc-content">{{ previewItem.desc }}</div>
        </div>

        <div class="audit-section">
          <h4>图片资源 ({{ previewItem.images?.length }}张)：</h4>
          <div class="img-grid">
            <el-image 
              v-for="img in previewItem.images" 
              :key="img" 
              :src="'http://127.0.0.1:8000' + img" 
              :preview-src-list="previewItem.images.map(i => 'http://127.0.0.1:8000' + i)"
              fit="cover" 
              class="preview-img"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="auditPreviewVisible = false">关闭预览</el-button>
        <el-button type="danger" @click="handleAudit(previewItem.id, 'off')">拒绝申请</el-button>
        <el-button type="success" @click="handleAudit(previewItem.id, 'onsale')">准予上架</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { Money, ShoppingCart, Warning, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const auditPreviewVisible = ref(false)
const previewItem = ref(null)
const lineChartRef = ref(null)
const pieChartRef = ref(null)
const auditList = ref([])
const metrics = reactive({ total_gmv: 0, total_orders: 0, pending_audit: 0 })

const statsCards = computed(() => [
  { title: '平台总成交额', value: metrics.total_gmv, prefix: '￥', icon: Money, color: '#f56c6c', trend: 12.5 },
  { title: '全平台订单数', value: metrics.total_orders, prefix: '', icon: ShoppingCart, color: '#409eff', trend: 8.2 },
  { title: '待审核商品', value: metrics.pending_audit, prefix: '', icon: Warning, color: '#e6a23c', trend: -2.1 },
  { title: '新增活跃用户', value: 128, prefix: '', icon: User, color: '#67c23a', trend: 24.0 },
])

const initCharts = (data) => {
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.trend.map(i => i.day.split('T')[0]) },
    yAxis: { type: 'value' },
    series: [{ data: data.trend.map(i => i.amount), type: 'line', smooth: true, areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }, itemStyle: { color: '#409eff' } }]
  })

  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b} : {c} 件 ({d}%)' },
    legend: { orient: 'vertical', left: 'left', type: 'scroll' },
    color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    series: [{
      type: 'pie', radius: ['45%', '70%'], avoidLabelOverlap: true,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, position: 'outside', formatter: '{b}\n{d}%' },
      data: data.categories.map(i => ({ name: i.name, value: i.prod_count }))
    }]
  })
}

// 核心刷新逻辑
const refreshDashboardData = async () => {
  try {
    const [statsRes, prodRes] = await Promise.all([
      request({ url: '/trade/admin/dashboard/', method: 'get' }),
      request({ url: '/goods/list/?status=audit&mine=0', method: 'get' })
    ])
    Object.assign(metrics, statsRes.metrics)
    auditList.value = prodRes.results || prodRes
    initCharts(statsRes)
  } catch (err) {
    console.error('数据刷新失败', err)
  }
}

// 🚀 修正 2：修复 handleAudit 重复定义错误
const handleAudit = async (id, status) => {
  try {
    await request({ 
      url: `/goods/list/${id}/change_status/`, 
      method: 'post', 
      data: { status: status } 
    })

    auditList.value = auditList.value.filter(item => item.id !== id)
    ElMessage.success(status === 'onsale' ? '审核通过' : '已拒绝申请')
    
    // 操作完关闭弹窗
    auditPreviewVisible.value = false

    setTimeout(() => {
      refreshDashboardData()
    }, 300)
  } catch (err) {
    console.error('审核失败', err)
  }
}

// 打开预览弹窗
const openAuditPreview = (row) => {
  previewItem.value = row // 🚀 修正：现在 row 是完整对象了
  auditPreviewVisible.value = true
}

onMounted(() => {
  refreshDashboardData()
})
</script>

<style scoped lang="scss">
.admin-dashboard { padding: 20px; background-color: #f0f2f5; }
.stat-card { position: relative; .value { font-size: 24px; font-weight: bold; } .card-icon { position: absolute; right: 20px; top: 20px; font-size: 40px; opacity: 0.2; } }

/* 🚀 补充企业级审计样式 */
.audit-panel {
  max-height: 65vh;
  overflow-y: auto;
  padding: 10px;
  .audit-section {
    margin-top: 20px;
    h4 { border-left: 4px solid #409eff; padding-left: 10px; margin-bottom: 10px; color: #333; }
    .desc-content { background: #f8f9fa; padding: 15px; border-radius: 4px; line-height: 1.6; white-space: pre-wrap; color: #666; }
    .img-grid { display: flex; flex-wrap: wrap; gap: 10px; .preview-img { width: 120px; height: 120px; border-radius: 4px; border: 1px solid #eee; } }
  }
}
</style>