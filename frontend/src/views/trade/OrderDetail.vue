<template>
  <div class="order-detail-page">
    <!-- 🚀 1. 无论什么状态，返回按钮必须在，防止用户“困死”在白屏页 -->
    <el-page-header @back="$router.push('/user/orders')" content="订单单据详情" style="margin-bottom: 20px;" />

    <!-- 🚀 2. 加载中状态：显示骨架屏 -->
    <div v-if="loading" style="padding: 40px">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 🚀 3. 加载失败状态：显示空状态，并给出提示 -->
    <el-empty v-else-if="!order.id" description="未找到该订单信息，请返回列表重试">
      <el-button type="primary" @click="$router.push('/user/orders')">回到订单列表</el-button>
    </el-empty>

    <!-- 🚀 4. 加载成功：显示核心内容 (原有的逻辑) -->
    <el-card v-else class="detail-card">
      <div class="status-banner">
        <el-icon :size="40" color="#409EFF"><InfoFilled /></el-icon>
        <div class="status-text">
          <p class="label">当前订单状态</p>
          <p class="value">{{ statusMap[order.status]?.label || '处理中' }}</p>
        </div>
      </div>

      <el-descriptions title="交易信息" :column="2" border>
        <el-descriptions-item label="订单编号">{{ order.order_sn }}</el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ formatDate(order.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="支付时间">{{ order.pay_time ? formatDate(order.pay_time) : '未支付' }}</el-descriptions-item>
        <el-descriptions-item label="交易金额"><span class="price">￥{{ order.total_amount }}</span></el-descriptions-item>
      </el-descriptions>

      <el-descriptions title="收货信息" :column="1" border style="margin-top: 25px">
        <el-descriptions-item label="收货人">{{ order.receiver_info?.receiver || '无' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ order.receiver_info?.mobile || '无' }}</el-descriptions-item>
        <el-descriptions-item label="详细地址">
          {{ order.receiver_info?.region }} {{ order.receiver_info?.detail }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="product-snapshot" style="margin-top: 25px">
        <h4 style="margin-bottom: 15px">商品快照</h4>
        <div class="prod-box" @click="$router.push('/product/'+order.product)">
          <el-image :src="'http://127.0.0.1:8000' + order.product_image" class="p-img" />
          <div class="p-info">
            <p class="p-title">{{ order.product_title }}</p>
            <p class="p-seller">卖家：{{ order.seller_name }}</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const order = ref({})
const loading = ref(true) // 🚀 新增加载状态

const statusMap = {
  unpaid: { label: '待支付', type: 'warning' },
  paid: { label: '已支付/待发货', type: 'success' },
  shipped: { label: '已发货/待收货', type: 'primary' },
  received: { label: '交易完成', type: 'info' },
  closed: { label: '已关闭', type: 'danger' }
}

const fetchDetail = async () => {
  const orderId = route.params.id
  console.log("OrderDetail 正在尝试请求 ID:", orderId)

  if (!orderId || orderId === 'undefined') {
    loading.value = false
    return ElMessage.error('订单路径参数无效')
  }

  try {
    loading.value = true
    const res = await request({ url: `/trade/orders/${orderId}/`, method: 'get' })
    console.log('后端返回的详情:', res)
    order.value = res
  } catch (err) {
    console.error('详情页获取失败:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (d) => d ? new Date(d).toLocaleString() : '-'

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped lang="scss">
.order-detail-page { max-width: 900px; margin: 20px auto; padding: 20px; }
.status-banner { display: flex; align-items: center; gap: 15px; background: #ecf5ff; padding: 20px; border-radius: 8px; margin-bottom: 25px;
  .status-text { .label { font-size: 13px; color: #666; margin: 0; } .value { font-size: 20px; font-weight: bold; color: #409eff; margin: 5px 0 0; } }
}
.price { color: #f56c6c; font-weight: bold; font-size: 18px; }
.prod-box { display: flex; align-items: center; padding: 15px; border: 1px solid #eee; border-radius: 8px; cursor: pointer;
  &:hover { background: #fafafa; }
  .p-img { width: 60px; height: 60px; border-radius: 4px; margin-right: 15px; }
  .p-title { font-weight: bold; margin: 0; }
  .p-seller { font-size: 12px; color: #999; margin: 5px 0 0; }
}
</style>

