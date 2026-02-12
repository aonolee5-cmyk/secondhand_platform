<template>
  <div class="order-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="我买到的" name="buy">
        <el-table :data="buyOrders">
          <el-table-column prop="order_sn" label="订单号" width="180" />
          <el-table-column prop="product_title" label="商品" />
          <el-table-column prop="total_amount" label="金额" />
          <el-table-column label="状态">
            <template #default="scope">
              <el-tag>{{ statusMap[scope.row.status] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <!-- 待支付状态显示去支付 -->
              <el-button v-if="scope.row.status==='unpaid'" type="warning" @click="handlePay(scope.row.id)">去支付</el-button>
              
              <!-- 已发货状态显示确认收货 -->
              <el-button v-if="scope.row.status==='shipped'" type="success" @click="handleReceive(scope.row.id)">确认收货</el-button>
              
              <!-- 【新增】已收货状态显示去评价 -->
              <el-button v-if="scope.row.status==='received'" type="primary" @click="openReview(scope.row)">去评价</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="我卖出的" name="sell">
         <!-- 卖家逻辑：发货等 -->
      </el-tab-pane>
    </el-tabs>

    <!-- 【新增】评价弹窗 -->
    <el-dialog v-model="reviewVisible" title="评价这次交易" width="400px">
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="评分">
          <!-- Element Plus 的评分组件 -->
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue' // 【新增】引入 reactive
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const activeTab = ref('buy')
const buyOrders = ref([])

// 【新增】评价相关的响应式数据
const reviewVisible = ref(false)
const reviewLoading = ref(false)
const currentOrderId = ref(null)
const reviewForm = reactive({
  buyer_score: 5,
  buyer_comment: ''
})

const statusMap = {
  'unpaid': '待支付',
  'paid': '已支付',
  'shipped': '已发货',
  'received': '已收货',
  'closed': '已关闭',
  'dispute': '异常/纠纷'
}

const loadOrders = async () => {
  const res = await request({ url: '/trade/orders/', method: 'get' })
  buyOrders.value = res.results || res
}

onMounted(loadOrders)

const handlePay = async (id) => {
  await request({ url: `/trade/orders/${id}/pay/`, method: 'post' })
  ElMessage.success('支付成功')
  loadOrders()
}

const handleReceive = async (id) => {
  await request({ url: `/trade/orders/${id}/receive/`, method: 'post' })
  ElMessage.success('已确认收货，交易完成')
  loadOrders()
}

// 【新增】打开评价弹窗
const openReview = (row) => {
  currentOrderId.value = row.id
  reviewForm.buyer_score = 5
  reviewForm.buyer_comment = ''
  reviewVisible.value = true
}

// 【新增】提交评价到后端
const submitReview = async () => {
  if (!reviewForm.buyer_comment) {
    ElMessage.warning('写点评价内容吧')
    return
  }
  
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
    ElMessage.success('评价成功，卖家信用分已更新！')
    reviewVisible.value = false
    loadOrders() // 刷新列表，评价后按钮会根据业务逻辑消失
  } catch (err) {
    console.error(err)
  } finally {
    reviewLoading.value = false
  }
}
</script>

<style scoped>
.order-container { padding: 20px; }
</style>