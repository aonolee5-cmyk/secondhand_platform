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
       <!-- 这里放入之前写的 Product 管理逻辑，但使用更高级的表格设计 -->
       <el-table :data="auditList" stripe>
         <el-table-column prop="title" label="商品名称" />
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
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { Money, ShoppingCart, Warning, User } from '@element-plus/icons-vue'

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
  // 折线图初始化逻辑
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.trend.map(i => i.day.split('T')[0]) },
    yAxis: { type: 'value' },
    series: [{ 
      data: data.trend.map(i => i.amount), 
      type: 'line', 
      smooth: true, 
      areaStyle: { color: 'rgba(64, 158, 255, 0.1)' },
      itemStyle: { color: '#409eff' }
    }]
  })

  // 饼图初始化逻辑
  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.categories.map(i => ({ name: i.name, value: i.prod_count })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  })
}

onMounted(async () => {
  const res = await request({ url: '/trade/admin/dashboard/', method: 'get' })
  Object.assign(metrics, res.metrics)
  initCharts(res)
  
  // 加载待审核商品 (复用之前的商品接口，传 status=audit)
  const prodRes = await request({ url: '/goods/list/?status=audit', method: 'get' })
  auditList.value = prodRes.results || prodRes
})
</script>

<style scoped lang="scss">
.admin-dashboard {
  background-color: #f0f2f5;
  padding: 24px;
  min-height: 100vh;
}
.stat-card {
  position: relative;
  .title { color: #999; font-size: 14px; margin-bottom: 8px; }
  .value { font-size: 24px; font-weight: bold; color: #333; }
  .footer { margin-top: 10px; font-size: 12px; color: #999; .up { color: #f56c6c; } .down { color: #67c23a; } }
  .card-icon { position: absolute; right: 20px; top: 20px; font-size: 40px; opacity: 0.15; }
}
</style>