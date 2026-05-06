<template>
  <div class="admin-dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statsCards" :key="card.title">
        <el-card shadow="hover" class="stat-card">
          <div class="card-content">
            <div class="title">{{ card.title }}</div>
            <div class="value">{{ card.prefix }}{{ card.value }}</div>
            <div class="footer">当前统计时段</div>
          </div>
          <el-icon class="card-icon" :color="card.color"><component :is="card.icon" /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 25px">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold;">平台交易趋势分析</span>
              <div class="header-actions" style="display: flex; align-items: center; gap: 8px;">
              <el-date-picker
                v-model="startDate"
                type="date"
                placeholder="开始日期"
                value-format="YYYY-MM-DD"
                size="small"
                style="width: 135px"
              />
              <span style="color: #999; font-size: 12px">至</span>
              <el-date-picker
                v-model="endDate"
                type="date"
                placeholder="结束日期"
                value-format="YYYY-MM-DD"
                size="small"
                style="width: 135px"
              />
              
              <el-button 
                type="primary" 
                size="small" 
                icon="Search"
                @click="handleManualSearch"
              >确认查询</el-button>
              
              <el-button size="small" link @click="resetToSevenDays">重置</el-button>
            </div>
            </div>
          </template>
          <div ref="lineChartRef" style="height: 380px"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card header="全平台品类分布" shadow="never">
          <div ref="pieChartRef" style="height: 380px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待办任务：待审核商品列表 -->
    <el-card header="待审核商品列表" style="margin-top: 25px" shadow="never">
       <el-table :data="auditList" stripe>
         <el-table-column label="商品名称">
          <template #default="scope">
            <el-link type="primary" :underline="false" @click="openAuditPreview(scope.row)">
              {{ scope.row.title }}
            </el-link>
          </template>
        </el-table-column>
         <el-table-column prop="owner_name" label="发布者" />
         <el-table-column prop="price" label="售价" width="100" />
         <el-table-column label="操作" width="150">
           <template #default="scope">
             <el-button type="success" size="small" @click="handleAudit(scope.row.id, 'onsale')">通过</el-button>
             <el-button type="danger" size="small" @click="handleAudit(scope.row.id, 'off')">拒绝</el-button>
           </template>
         </el-table-column>
       </el-table>
    </el-card>

    <!-- 审计弹窗 -->
    <el-dialog v-model="auditPreviewVisible" title="商品参数审计" width="750px" destroy-on-close>
       <!-- ... -->
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, shallowRef } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { Money, ShoppingCart, Warning, User, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const auditPreviewVisible = ref(false)
const previewItem = ref(null)
const lineChartRef = ref(null)
const pieChartRef = ref(null)
const auditList = ref([])
const metrics = reactive({ total_gmv: 0, total_orders: 0, pending_audit: 0 })
const charts = shallowRef({ line: null, pie: null })

const startDate = ref('')
const endDate = ref('')
// 搜索函数
const handleManualSearch = () => {
  if (startDate.value && endDate.value) {
    // 简单校验
    if (new Date(startDate.value) > new Date(endDate.value)) {
      ElMessage.warning('开始日期不能晚于结束日期')
      return
    }
    // 调用刷新函数，传入选中的日期
    refreshDashboardData(startDate.value, endDate.value)
  } else {
    ElMessage.warning('请同时选择开始和结束日期')
  }
}



const statsCards = computed(() => [
  { title: '平台总成交额', value: metrics.total_gmv, prefix: '￥', icon: Money, color: '#f56c6c' },
  { title: '全平台订单数', value: metrics.total_orders, prefix: '', icon: ShoppingCart, color: '#409eff' },
  { title: '待审核商品', value: metrics.pending_audit, prefix: '', icon: Warning, color: '#e6a23c' },
  { title: '新增活跃用户', value: 128, prefix: '', icon: User, color: '#67c23a' },
])

const initCharts = (data) => {
  
  if (!data.trend || data.trend.length === 0) {
     console.warn("选定范围内无交易数据");
  }

  //  折线图 
  if (!charts.value.line) charts.value.line = echarts.init(lineChartRef.value)
  
  charts.value.line.setOption({
    // 提示框保持开启
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'cross' } 
    },
    

    grid: { 
      left: '3%', 
      right: '4%', 
      bottom: '5%', 
      containLabel: true 
    },

    xAxis: { 
      type: 'category', 
      boundaryGap: false, 
      data: data.trend.map(i => i.day.split('T')[0]) 
    },

    yAxis: { 
      type: 'value', 
      name: '成交金额 (元)' 
    },

    series: [{
      name: '交易额',
      data: data.trend.map(i => i.amount),
      type: 'line',
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64,158,255,0.4)' },
          { offset: 1, color: 'rgba(64,158,255,0)' }
        ]) 
      }
    }]
  }, true) 
  
  // --- 饼图 ---
  if (!charts.value.pie) charts.value.pie = echarts.init(pieChartRef.value)
  const totalItems = data.categories.reduce((a, b) => a + b.prod_count, 0)
  charts.value.pie.setOption({
    tooltip: { trigger: 'item', formatter: '{b} : {c}件 ({d}%)' },
    legend: { type: 'scroll', orient: 'vertical', left: 'left', top: 'center' },
    color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    series: [{
      name: '品类占比', type: 'pie', radius: ['45%', '70%'], avoidLabelOverlap: true,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, position: 'outside', formatter: '{b}\n{d}%' },
      data: data.categories.map(i => ({ name: i.name, value: i.prod_count }))
    }],
    graphic: {
      type: 'text', left: 'center', top: 'center',
      style: { text: '商品总计\n' + totalItems, textAlign: 'center', fill: '#333', fontSize: 14, fontWeight: 'bold' }
    }
  })
}

// --- 业务逻辑 ---
const refreshDashboardData = async (start = '', end = '') => {
  try {
    const [statsRes, prodRes] = await Promise.all([
      // 向后端传递日期范围
      request({ 
        url: '/trade/admin/dashboard/', 
        method: 'get',
        params: { start_date: start, end_date: end } 
      }),
      request({ url: '/goods/list/?status=audit&mine=0', method: 'get' })
    ])
    Object.assign(metrics, statsRes.metrics)
    auditList.value = prodRes.results || prodRes
    initCharts(statsRes)
  } catch (err) {
    console.error('数据刷新失败', err)
  }
}


const resetToSevenDays = () => {
  startDate.value = ''
  endDate.value = ''
  refreshDashboardData()
}

const handleAudit = async (id, status) => {
  try {
    await request({ url: `/goods/list/${id}/change_status/`, method: 'post', data: { status: status } })
    auditList.value = auditList.value.filter(item => item.id !== id)
    ElMessage.success('审核处理完成')
    auditPreviewVisible.value = false
    setTimeout(() => refreshDashboardData(dateRange.value?.[0], dateRange.value?.[1]), 400)
  } catch (err) { console.error(err) }
}

const openAuditPreview = (row) => { previewItem.value = row; auditPreviewVisible.value = true; }

onMounted(() => {
  refreshDashboardData()
  window.addEventListener('resize', () => {
    charts.value.line?.resize()
    charts.value.pie?.resize()
  })
})
</script>


<style scoped lang="scss">
.admin-dashboard { padding: 20px; background-color: #f0f2f5; min-height: 100vh; }
.stat-card { position: relative; padding: 5px; .value { font-size: 24px; font-weight: bold; margin: 10px 0; } .card-icon { position: absolute; right: 20px; top: 20px; font-size: 45px; opacity: 0.1; } .footer { font-size: 12px; color: #999; } }
.audit-panel { max-height: 65vh; overflow-y: auto; .audit-section { margin-top: 20px; h4 { border-left: 4px solid #409eff; padding-left: 10px; margin-bottom: 10px; } .desc-content { background: #f8f9fa; padding: 15px; border-radius: 4px; white-space: pre-wrap; } .img-grid { display: flex; flex-wrap: wrap; gap: 10px; .preview-img { width: 120px; height: 120px; border-radius: 4px; border: 1px solid #eee; } } } }
</style>