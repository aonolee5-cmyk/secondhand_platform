<!-- frontend/src/views/admin/OrderList.vue -->
<template>
  <div class="admin-order-list">
    <el-card shadow="never">
      <template #header>
        <div class="header-title">
          <el-icon><Judge /></el-icon>
          <span style="margin-left: 8px; font-weight: bold;">纠纷处理</span>
        </div>
      </template>

      <div class="filter-bar">
        <el-radio-group v-model="statusFilter" @change="fetchOrders">
          <el-radio-button value="arbitrating">待处理订单</el-radio-button>
          <el-radio-button value="closed">已关闭记录</el-radio-button>
          <el-radio-button value="">全部订单</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="orders" stripe style="width: 100%; margin-top: 20px" v-loading="loading">
        <el-table-column label="订单号" width="200">
          <template #default="scope">
            <el-link type="primary" :underline="false" @click="openOrderDetail(scope.row)">
              {{ scope.row.order_sn }}
            </el-link>
          </template>
        </el-table-column>
          
        <el-table-column prop="product_title" label="涉及商品" />
        <el-table-column prop="total_amount" label="交易金额" width="100">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold;">￥{{ scope.row.total_amount }}</span>
          </template>
        </el-table-column>
      
        <el-table-column prop="refund_reason" label="申诉原由" show-overflow-tooltip />

        <el-table-column label="当前环节" width="120">
          <template #default="scope">
            <el-tag :type="statusMap[scope.row.status]?.type || 'info'">
              {{ statusMap[scope.row.status]?.label || scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="管理决策" width="150" align="center">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'arbitrating'" 
              type="danger" 
              size="small" 
              @click="openArbitrate(scope.row)"
            >
              执行判决
            </el-button>
            <span v-else style="color: #999; font-size: 12px;">无需介入</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>


    <el-dialog v-model="detailVisible" title="交易数据存证" width="800px" top="5vh">
      <div v-if="selectedOrder" class="admin-order-detail">
        <el-alert 
          :title="'当前订单状态：' + statusMap[selectedOrder.status]?.label" 
          :type="selectedOrder.status === 'arbitrating' ? 'warning' : 'info'"
          show-icon :closable="false"
          style="margin-bottom: 20px"
        />

        <el-row :gutter="20">
          <el-col :span="12">
            <el-descriptions title="基础信息" :column="1" border>
              <el-descriptions-item label="订单 ID">{{ selectedOrder.id }}</el-descriptions-item>
              <el-descriptions-item label="下单时间">{{ formatDate(selectedOrder.create_time) }}</el-descriptions-item>
              <el-descriptions-item label="支付金额"><b style="color: #f56c6c">￥{{ selectedOrder.total_amount }}</b></el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <el-descriptions title="交易主体" :column="1" border>
              <el-descriptions-item label="卖家账号">{{ selectedOrder.seller_name }}</el-descriptions-item>
              <el-descriptions-item label="买家账号">{{ selectedOrder.buyer_name }}</el-descriptions-item>
              <el-descriptions-item label="收货人">{{ selectedOrder.receiver_info?.receiver }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <el-descriptions title="下单地址快照" :column="1" border style="margin-top: 20px">
          <el-descriptions-item label="联系电话">{{ selectedOrder.receiver_info?.mobile }}</el-descriptions-item>
          <el-descriptions-item label="详细地址">
            {{ selectedOrder.receiver_info?.region }} {{ selectedOrder.receiver_info?.detail }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedOrder.refund_reason" class="reason-content-box">
          <h4 style="color: #F56C6C; margin: 20px 0 10px;">纠纷申诉证据</h4>
          <div style="background: #fff5f5; padding: 15px; border-radius: 4px; border-left: 4px solid #f56c6c; color: #666;">
            <b>买家陈述：</b> {{ selectedOrder.refund_reason }}
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭预览</el-button>
        <template v-if="selectedOrder?.status === 'arbitrating'">
          <el-button type="danger" @click="handleArbitrateFromDetail('refund')">判决退款</el-button>
          <el-button type="success" @click="handleArbitrateFromDetail('pay_seller')">判决支付</el-button>
        </template>
      </template>
    </el-dialog>

    <!-- 仲裁判决对话框  -->
    <el-dialog v-model="dialogVisible" title=" 平台人工仲裁中心" width="500px" destroy-on-close>
      <div class="dispute-detail" v-if="currentOrder">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="买家账号">{{ currentOrder.buyer_name }}</el-descriptions-item>
          <el-descriptions-item label="卖家账号">{{ currentOrder.seller_name }}</el-descriptions-item>
          <el-descriptions-item label="退款原由">
            <b style="color: #E6A23C;">{{ currentOrder.refund_reason || '未填写' }}</b>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="center">判决处理</el-divider>
        <el-alert 
          title="仲裁说明：判决退款将原路返还金额并重新上架宝贝；判决支付将强制放款给卖家。" 
          type="warning" 
          :closable="false" 
          show-icon 
          style="margin-bottom: 20px" 
        />
      </div>
      <template #footer>
        <div style="display: flex; justify-content: space-between; width: 100%;">
          <el-button @click="dialogVisible = false">暂缓处理</el-button>
          <div class="btns">
             <el-button type="danger" @click="handleArbitrate('refund')">判决退款</el-button>
             <el-button type="success" @click="handleArbitrate('pay_seller')">判决支付</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const orders = ref([])
const statusFilter = ref('arbitrating')
const dialogVisible = ref(false)
const currentOrder = ref(null)
const loading = ref(false)


const detailVisible = ref(false)
const selectedOrder = ref(null)

const statusMap = {
  'unpaid': { label: '待支付', type: 'warning' },
  'paid': { label: '已支付', type: 'success' },
  'shipped': { label: '已发货', type: 'primary' },
  'received': { label: '交易完成', type: 'info' },
  'closed': { label: '已关闭', type: 'danger' },
  'dispute': { label: '买卖协商中', type: 'danger' },
  'arbitrating': { label: '平台仲裁中', type: 'warning' }
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await request({ 
      url: '/trade/admin/orders/', 
      method: 'get', 
      params: { status: statusFilter.value } 
    })
    orders.value = res.results || res
  } finally {
    loading.value = false
  }
}


const openOrderDetail = (row) => {
  selectedOrder.value = row
  detailVisible.value = true
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

const openArbitrate = (row) => {
  currentOrder.value = row
  dialogVisible.value = true
}


const handleArbitrateFromDetail = async (decision) => {
  currentOrder.value = selectedOrder.value
  await handleArbitrate(decision)
  detailVisible.value = false
}

const handleArbitrate = async (decision) => {
  try {
    await request({
      url: `/trade/admin/orders/${currentOrder.value.id}/arbitrate/`,
      method: 'post',
      data: { decision }
    })
    ElMessage.success('判决已生效，系统已自动调账')
    dialogVisible.value = false
    fetchOrders() 
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchOrders)
</script>

<style scoped>
.filter-bar { margin-bottom: 20px; }
.header-title { display: flex; align-items: center; font-size: 16px; }
.admin-order-detail { padding: 10px; }
</style>