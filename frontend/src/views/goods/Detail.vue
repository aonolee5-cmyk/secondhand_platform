<template>
  <div class="detail-container" v-if="product.id">
    <el-row :gutter="40">
      <!-- 左侧：图片轮播 -->
      <el-col :span="12">
        <el-carousel height="500px" border indicator-position="outside">
          <el-carousel-item v-for="(img, index) in product.images" :key="index">
            <el-image 
              :src="'http://127.0.0.1:8000' + img" 
              fit="contain" 
              class="main-img" 
              :preview-src-list="product.images.map(i => 'http://127.0.0.1:8000' + i)"
            />
          </el-carousel-item>
        </el-carousel>
      </el-col>

      <!-- 右侧：商品信息 -->
      <el-col :span="12">
        <div class="product-info">
          <h1 class="title">{{ product.title }}</h1>
          <div class="price-tag">
            <span class="symbol">￥</span>
            <span class="price">{{ product.price }}</span>
          </div>

          <el-divider />

          <!-- 卖家信息与信用展示 -->
          <div class="seller-box">
            <el-avatar :size="45" :src="product.owner_avatar ? 'http://127.0.0.1:8000' + product.owner_avatar : ''">
              <el-icon><UserFilled /></el-icon>
            </el-avatar>
            <div class="seller-info">
              <span class="name">卖家：{{ product.owner_name }}</span>
              <!-- 信用展示：结构图要求功能 -->
              <el-tag :color="creditLevel.color" effect="dark" style="border: none; color: white">
                {{ creditLevel.text }} ({{ product.owner_credit || 100 }})
              </el-tag>
            </div>
            <div class="chat-btn-mini">
               <el-button type="primary" size="small" plain icon="ChatDotRound">私聊</el-button>
            </div>
          </div>

          <p class="desc">{{ product.desc }}</p>

          <!-- 规格参数展示 (PostgreSQL JSONB 特性展示) -->
          <div class="attrs" v-if="product.attributes && Object.keys(product.attributes).length">
            <el-descriptions :column="1" border title="规格参数" size="small">
              <el-descriptions-item v-for="(val, key) in product.attributes" :key="key" :label="key">
                {{ val }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 核心交易按钮 -->
          <div class="actions">
            <el-button type="warning" size="large" icon="ChatDotRound" class="action-btn" @click="handleChat">向卖家咨询</el-button>
            <el-button type="danger" size="large" icon="ShoppingCart" class="action-btn" @click="handleBuy">立即购买</el-button>
            <el-button 
              :type="isFavorite ? 'danger' : 'info'" 
              :icon="isFavorite ? StarFilled : Star" 
              circle 
              size="large"
              @click="handleFavorite"
            />
          </div>

          <!-- 违规举报入口：放在右侧信息流底部，带虚线分割 -->
          <div class="report-section">
            <el-button link type="info" :icon="Warning" @click="reportVisible = true">
              <span class="report-text">商品违规或虚假信息？点击举报</span>
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 违规举报弹窗：工业级表单设计 -->
    <el-dialog v-model="reportVisible" title="违规举报" width="450px" destroy-on-close>
      <el-form :model="reportForm" label-position="top">
        <el-alert 
          title="恶意举报他人将被扣除信用分，请谨慎操作" 
          type="warning" 
          show-icon 
          :closable="false" 
          style="margin-bottom: 20px"
        />
        <el-form-item label="举报理由" required>
          <el-select v-model="reportForm.reason" placeholder="请选择举报原因" style="width: 100%">
            <el-option label="虚假信息/描述不符" value="fake" />
            <el-option label="诈骗/诱导线下交易" value="scam" />
            <el-option label="违禁物品" value="forbidden" />
            <el-option label="言语辱骂/不当言论" value="insult" />
            <el-option label="其他违规行为" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="详细说明（选填）">
          <el-input 
            v-model="reportForm.content" 
            type="textarea" 
            rows="4" 
            placeholder="请详细描述违规情况" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportVisible = false">取消</el-button>
        <el-button type="danger" @click="handleReportSubmit" :loading="reportLoading">提交举报</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProductDetail } from '@/api/goods'
import { submitReport } from '@/api/user' 
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, 
  ShoppingCart, 
  UserFilled, 
  Star, 
  StarFilled,
  Warning 
} from '@element-plus/icons-vue'

import {createOrder} from "@/api/trade";


const route = useRoute()
const router = useRouter()
const product = ref({})
const isFavorite = ref(false)
const reportDialog = ref({
  reason: '',
  content: '',
  target_user: null,
  product: null
})

// 咨询卖家逻辑
const handleChat = () => {
  console.log('咨询卖家')
  if (!localStorage.getItem('token')) {
    ElMessage.warning('请先登录再进行咨询')
    router.push('/login')
    return
  }
// 跳转到聊天页面
  router.push({
    name: 'Chat',
    params: { targetId: product.value.owner },
    query: { name: product.value.owner_name }
  })
}

// 信用展示逻辑
const creditLevel = computed(() => {
  const score = product.value.owner_credit || 100
  if (score >= 90) return { text: '信用极好', color: '#67C23A' }
  if (score >= 70) return { text: '信用良好', color: '#409EFF' }
  if (score >= 60) return { text: '信用一般', color: '#E6A23C' }
  return { text: '信用极差', color: '#F56C6C' }
})

// 收藏逻辑
const handleFavorite = () => {
  isFavorite.value = !isFavorite.value
  ElMessage.success(isFavorite.value ? '已加入收藏夹' : '已取消收藏')
}

// 举报逻辑
const reportVisible = ref(false)
const reportLoading = ref(false)
const reportForm = reactive({
  reason: '',
  content: ''
})

const handleReportSubmit = async () => {
  if (!reportForm.reason) {
    ElMessage.warning('请选择举报理由')
    return
  }
  
  reportLoading.value = true
  try {
    await submitReport({
      target_user: product.value.owner,
      product: product.value.id,
      reason: reportForm.reason,
      content: reportForm.content
    })
    
    ElMessageBox.alert('您的举报已收到，后台管理员将在24小时内审核处理。', '提交成功', {
      confirmButtonText: '确定',
      type: 'success',
      callback: () => {
        reportVisible.value = false
        reportForm.reason = ''
        reportForm.content = ''
      }
    })
  } catch (err) {
    console.error(err)
  } finally {
    reportLoading.value = false
  }
}

// 立即购买
const handleBuy = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录再进行购买')
    router.push('/login')
    return
  }
   try {
    await ElMessageBox.confirm(
      `商品价格：￥${product.value.price}，确定要下单吗？`,
      '交易确认',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 3. 调用后端下单 API
    // 注意：后端 createOrder 需要 product_id 和 address
    // 这里为了演示流程，我们先模拟一个默认地址对象
    // (完善版本应该弹窗让用户选择收货地址)
    const orderData = {
      product_id: product.value.id,
      address: {
        receiver: '当前用户', 
        mobile: '13800000000', 
        region: '线上交易', 
        detail: '无需配送' 
      }
    }

    await createOrder(orderData)
    
    // 4. 成功反馈
    ElMessage.success('下单成功！')
    
    // 5. 跳转到订单列表页去支付
    router.push('/orders')

  } catch (err) {
    // 捕获“取消”操作或后端报错
    if (err !== 'cancel') {
      console.error(err)
    }
  }
}

onMounted(async () => {
  const id = route.params.id
  const res = await getProductDetail(id)
  product.value = res
})
</script>

<style scoped>
.detail-container { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 40px 20px; 
}

.main-img { 
  width: 100%; 
  height: 500px; 
  border-radius: 8px; 
  cursor: zoom-in;
}

.product-info {
  display: flex;
  flex-direction: column;
}

.title { 
  font-size: 26px; 
  line-height: 1.4; 
  margin-bottom: 15px; 
  color: #2c3e50; 
  font-weight: 600;
}

.price-tag { 
  color: #f56c6c; 
  margin-bottom: 20px; 
  display: flex;
  align-items: baseline;
}

.symbol { font-size: 20px; font-weight: bold; }
.price { font-size: 38px; font-weight: 800; margin-left: 4px; }

.seller-box { 
  display: flex; 
  align-items: center; 
  margin-bottom: 30px; 
  background: #fdfdfd; 
  padding: 16px; 
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.seller-info { 
  margin-left: 15px; 
  flex: 1;
}

.name { 
  display: block; 
  font-weight: 600; 
  margin-bottom: 6px; 
  color: #333; 
}

.desc { 
  line-height: 1.8; 
  color: #555; 
  margin-bottom: 30px; 
  white-space: pre-wrap; 
  background: #fafafa; 
  padding: 20px; 
  border-radius: 8px;
  font-size: 15px;
}

.attrs { margin-bottom: 30px; }

.actions { 
  margin-top: 20px; 
  display: flex; 
  gap: 16px; 
  align-items: center; 
}

.action-btn {
  flex: 1;
  height: 50px;
  font-size: 16px;
  font-weight: bold;
}

.report-section { 
  margin-top: 40px; 
  border-top: 1px dashed #eee; 
  padding-top: 15px; 
  text-align: right;
}

.report-text {
  font-size: 13px;
  color: #999;
}

.report-text:hover {
  color: #f56c6c;
}

:deep(.el-carousel__indicators--outside) {
  margin-top: 10px;
}
</style>