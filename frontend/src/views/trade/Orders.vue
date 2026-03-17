<template>
  <div class="order-container">
    <el-tabs v-model="activeTab">
      
      <!-- ================= 买家视角 ================= -->
      <el-tab-pane label="我买到的" name="buy">
        <el-table :data="buyOrders" empty-text="暂无买入订单">
          <el-table-column prop="order_sn" label="订单号" width="180" />
          <el-table-column prop="product_title" label="商品" />
          <el-table-column prop="total_amount" label="金额" width="100" />
          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-tag :type="statusMap[scope.row.status].type">{{ statusMap[scope.row.status].label }}</el-tag>
              <div v-if="scope.row.status === 'dispute'" style="color: #F56C6C; font-size: 12px; margin-top: 5px;">
                处理中
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280">
            <template #default="scope">
              <el-button v-if="scope.row.status==='unpaid'" size="small" type="warning" @click="handlePay(scope.row.id)">去支付</el-button>
              <el-button v-if="scope.row.status==='shipped'" size="small" type="success" @click="handleReceive(scope.row.id)">确认收货</el-button>
              
              <el-button 
                v-if="['paid', 'shipped'].includes(scope.row.status)" 
                size="small" type="danger" plain 
                @click="openRefund(scope.row.id)"
              >
                申请退款
              </el-button>
              <template v-if="scope.row.status === 'dispute'">
                <el-button size="small" type="primary" @click="applyArbitration(scope.row.id)">申请客服介入</el-button>
              </template>
              <el-button v-if="scope.row.status==='received'" size="small" type="primary" @click="openReview(scope.row)">去评价</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ================= 卖家视角 ================= -->
      <el-tab-pane label="我卖出的" name="sell">
        <el-table :data="sellOrders" empty-text="暂无卖出订单">
          <el-table-column prop="order_sn" label="订单号" width="180" />
          <el-table-column prop="product_title" label="商品" />
          <el-table-column prop="total_amount" label="金额" width="100" />
          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-tag :type="statusMap[scope.row.status].type">{{ statusMap[scope.row.status].label }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280">
            <template #default="scope">
              <el-button v-if="scope.row.status==='paid'" size="small" type="primary" @click="handleShip(scope.row.id)">去发货</el-button>
              
              <template v-if="scope.row.status==='dispute'">
                <el-button size="small" type="success" @click="processRefund(scope.row.id, 'agree')">同意退款</el-button>
                <el-button size="small" type="danger" @click="processRefund(scope.row.id, 'reject')">拒绝退款</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>


          <!-- 买家端操作列 -->
          <!-- <template v-if="scope.row.status === 'dispute'">
            <el-button size="small" type="primary" @click="applyArbitration(scope.row.id)">申请客服介入</el-button>
          </template> -->
    </el-tabs>

    <!-- 评价弹窗 -->
    <el-dialog v-model="reviewVisible" title="评价这次交易" width="400px">
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="评分">
          <el-rate v-model="reviewForm.buyer_score" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input 
            v-model="reviewForm.buyer_comment" 
            type="textarea" 
            :rows="3" 
            placeholder="说说你的交易感受吧，您的评价将影响卖家的信用分..." 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="reviewLoading">提交评价</el-button>
      </template>
    </el-dialog>

    <!-- 退款弹窗 -->
    <el-dialog v-model="refundVisible" title="申请退款/退换货" width="400px">
      <el-form :model="refundForm" label-position="top">
        <el-form-item label="请选择退款原因" required>
          <el-select v-model="refundForm.reason" placeholder="请选择原因" style="width: 100%" @change="handleReasonChange">
            <el-option label="商品描述不符" value="商品描述不符" />
            <el-option label="质量问题/有损坏" value="质量问题/有损坏" />
            <el-option label="不想要了/拍错了" value="不想要了/拍错了" />
            <el-option label="卖家一直未发货" value="卖家一直未发货" />
            <el-option label="其他原因" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="详细说明" v-if="showCustomReason" required>
          <el-input 
            v-model="refundForm.customContent" 
            type="textarea" 
            rows="3" 
            placeholder="请填写您的具体原因..." 
          />
          </el-form-item>
        </el-form>
      <template #footer>
        <el-button @click="refundVisible = false">取消</el-button>
        <el-button type="danger" @click="submitRefund" :loading="refundLoading">确认申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { getProfile } from '@/api/user' 
import { ElMessage } from 'element-plus'

const activeTab = ref('buy')
const buyOrders = ref([])
const sellOrders = ref([])

const refundVisible = ref(false)
const refundLoading = ref(false)
const refundOrderId = ref(null)
const showCustomReason = ref(false)
const refundForm = reactive({ reason: '', customContent: ''})

const reviewVisible = ref(false)
const reviewLoading = ref(false)
const currentOrderId = ref(null)
const reviewForm = reactive({ buyer_score: 5, buyer_comment: '' })

const statusMap = {
  'unpaid': { label: '待支付', type: 'warning' },
  'paid': { label: '已支付', type: 'success' },
  'shipped': { label: '已发货', type: 'primary' },
  'received': { label: '交易完成', type: 'info' },
  'closed': { label: '已关闭', type: 'danger' },
  'dispute': { label: '纠纷中', type: 'danger' },
  'arbitrating': { label:'客服介入中', type: 'info' }
}

const handleReasonChange = (val) => {
  showCustomReason.value = (val === 'other')
  if (val !== 'other') refundForm.customContent = ''
}

const loadOrders = async () => {
  const profile = await getProfile() 
  const res = await request({ url: '/trade/orders/', method: 'get' })
  const allOrders = res.results || res
  buyOrders.value = allOrders.filter(o => o.buyer === profile.id)
  sellOrders.value = allOrders.filter(o => o.seller === profile.id)
}

const handlePay = async (id) => {
  await request({ 
    url: `/trade/orders/${id}/pay/`,
    method: 'post' 
    })
  ElMessage.success('支付成功')
  loadOrders()
}

const handleReceive = async (id) => {
  await request({ 
  url: `/trade/orders/${id}/receive/`,
  method: 'post' })
  ElMessage.success('已确认收货')
  loadOrders()
}

const handleShip = async (id) => {
  await request({
  url: `/trade/orders/${id}/ship/`,
  method: 'post' })
  ElMessage.success('发货成功')
  loadOrders()
}

const openRefund = (id) => {
  refundOrderId.value = id
  refundVisible.value = true
}

const submitRefund = async () => {
  let finalReason = refundForm.reason
  if (refundForm.reason === 'other') {
    if (!refundForm.customContent) return ElMessage.warning('请填写具体原因')
    finalReason = `其他：${refundForm.customContent}`
  } else if (!refundForm.reason) {
    return ElMessage.warning('请选择原因')
  }

  refundLoading.value = true
  try {
    await request({ 
      url: `/trade/orders/${refundOrderId.value}/apply_refund/`, 
      method: 'post', 
      data: { reason: finalReason } 
    })
    ElMessage.success('退款申请已提交')
    refundVisible.value = false
    loadOrders()
  } finally {
    refundLoading.value = false
  }
}

const processRefund = async (id, action) => {
  await request({ 
    url: `/trade/orders/${id}/handle_refund/`, 
    method: 'post', 
    data: { action } 
  })
  ElMessage.success(action === 'agree' ? '已同意退款' : '已拒绝退款')
  loadOrders()
}

const openReview = (row) => {
  currentOrderId.value = row.id
  reviewVisible.value = true
}

const submitReview = async () => {
  reviewLoading.value = true
  try {
    await request({ 
      url: '/trade/reviews/', 
      method: 'post', 
      data: {
        order: currentOrderId.value,
        buyer_score: reviewForm.buyer_score,
        buyer_comment: reviewForm.buyer_comment
      } 
    })
    ElMessage.success('评价成功！')
    reviewVisible.value = false
    loadOrders()
  } finally {
    reviewLoading.value = false
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.order-container { padding: 20px; }
.order-card { margin-bottom: 15px; }
.order-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
.order-content { display: flex; align-items: center; }
.prod-img { width: 60px; height: 60px; margin-right: 15px; border-radius: 4px; }
.info { flex: 1; }
.price { color: #f56c6c; font-weight: bold; }
</style>