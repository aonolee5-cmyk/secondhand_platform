<!-- frontend/src/views/admin/OrderList.vue -->
<template>
  <div class="admin-order-list">
    <el-card>
      <div class="filter-bar">
        <el-radio-group v-model="statusFilter" @change="fetchOrders">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="dispute">买家申请退款</el-radio-button>
          <el-radio-button value="arbitrating">待仲裁</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="orders" stripe style="margin-top: 20px">
        <el-table-column prop="order_sn" label="订单号" width="180" />
        <el-table-column prop="product_title" label="商品信息" />
        <el-table-column prop="total_amount" label="金额" width="100" />
        <el-table-column label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'arbitrating' ? 'danger' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button v-if="['dispute', 'arbitrating'].includes(scope.row.status)" 
              type="danger" size="small" @click="openArbitrate(scope.row)">
              介入仲裁
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 仲裁对话框 -->
    <el-dialog v-model="dialogVisible" title="客服人工仲裁中心" width="500px">
      <div class="dispute-detail" v-if="currentOrder">
        <p><strong>买家申诉理由：</strong> {{ currentOrder.refund_reason || '未填写' }}</p>
        <el-divider content-position="left">请做出判决</el-divider>
        <el-alert title="仲裁结果不可逆，请谨慎操作" type="warning" show-icon style="margin-bottom: 20px" />
      </div>
      <template #footer>
        <el-button type="success" @click="handleArbitrate('pay_seller')">判决买家支付 (打款给卖家)</el-button>
        <el-button type="danger" @click="handleArbitrate('refund')">判决退款 (款项回退买家)</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const orders = ref([])
const statusFilter = ref('')
const dialogVisible = ref(false)
const currentOrder = ref(null)

const fetchOrders = async () => {
  const res = await request({ 
    url: '/trade/admin/orders/', 
    method: 'get', 
    params: { status: statusFilter.value } 
  })
  orders.value = res.results || res
}

const openArbitrate = (row) => {
  currentOrder.value = row
  dialogVisible.value = true
}

const handleArbitrate = async (decision) => {
  await request({
    url: `/trade/admin/orders/${currentOrder.value.id}/arbitrate/`,
    method: 'post',
    data: { decision }
  })
  ElMessage.success('仲裁指令已下达，系统已自动调账')
  dialogVisible.value = false
  fetchOrders()
}

onMounted(fetchOrders)
</script>