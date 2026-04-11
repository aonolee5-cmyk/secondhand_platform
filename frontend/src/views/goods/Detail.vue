<template>
  <div class="detail-container" v-if="product.id">
    <el-row :gutter="40">
      <!-- 图片轮播 -->
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

      <!-- 商品信息 -->
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
              <!-- 信用展示 -->
              <el-tag :color="creditLevel.color" effect="dark" style="border: none; color: white">
                {{ creditLevel.text }} ({{ product.owner_credit || 100 }})
              </el-tag>
            </div>
          </div>

          <p class="desc">{{ product.desc }}</p>

          <!-- 规格参数展示  -->
          <div class="attrs" v-if="product.attributes && Object.keys(product.attributes).length">
            <el-descriptions :column="1" border title="规格参数" size="small">
              <el-descriptions-item v-for="(val, key) in product.attributes" :key="key" :label="key">
                {{ val }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 核心交易按钮 -->
          <div class="actions">
            <el-button type="warning" size="large" icon="ChatDotRound" class="action-btn" @click="handleChat">向商家咨询</el-button>
            <el-button type="primary" plain size="large" icon="ShoppingCart" class="action-btn"@click="handleAddToCart">加入购物车</el-button>
            <el-button type="danger" size="large" icon="ShoppingCart" class="action-btn" @click="handleBuy">立即购买</el-button>
            <el-button 
              :type="isFavorite ? 'danger' : 'info'" 
              :icon="isFavorite ? StarFilled : Star" 
              circle 
              size="large"
              @click="handleFavorite"
            />
          </div>

          <!-- 违规举报入口 -->
          <div class="report-section">
            <el-button link type="info" :icon="Warning" @click="reportVisible = true">
              <span class="report-text">商品违规或虚假信息？点击举报</span>
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 违规举报弹窗 -->
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
    <!-- 🚀 新增：地址选择弹窗 (企业级真实逻辑) -->
    <el-dialog v-model="addressVisible" title="确认收货信息" width="500px" destroy-on-close>
      <div class="address-selector-container">
        <el-alert 
          title="请选择一个收货地址以完成下单" 
          type="info" 
          show-icon 
          :closable="false" 
          style="margin-bottom: 15px"
        />
        
        <el-radio-group v-model="selectedAddressId" style="width: 100%">
          <div class="address-list-wrapper">
            <el-card 
              v-for="addr in addressList" 
              :key="addr.id" 
              :class="['addr-card', { active: selectedAddressId === addr.id }]"
              shadow="never"
              @click="selectedAddressId = addr.id"
            >
              <el-radio :value="addr.id">
                <div class="addr-detail">
                  <div class="top">
                    <span class="name">{{ addr.receiver }}</span>
                    <span class="phone">{{ addr.mobile }}</span>
                    <el-tag v-if="addr.is_default" size="small" type="danger" effect="plain">默认</el-tag>
                  </div>
                  <div class="bottom">
                    {{ addr.region }} {{ addr.detail }}
                  </div>
                </div>
              </el-radio>
            </el-card>
          </div>
        </el-radio-group>
      </div>

      <template #footer>
        <el-button @click="addressVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmOrder" :loading="orderLoading">确认购买</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProductDetail } from '@/api/goods'
import { submitReport, getAddresses } from '@/api/user' 
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, 
  ShoppingCart, 
  UserFilled, 
  Star, 
  StarFilled,
  Warning 
} from '@element-plus/icons-vue'
import {createOrder, checkFavoriteStatus, toggleFavorite} from "@/api/trade";
import request from '@/utils/request'
import { addToCart } from '@/api/trade'

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

const orderLoading = ref(false)

const addressVisible = ref(false)     // 控制地址选择弹窗
const addressList = ref([])           // 用户的所有地址
const selectedAddressId = ref(null)   // 用户选中的地址ID

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

// --- 2. 核心：收藏逻辑 (支持取消) ---
// 初始化时检查是否已收藏
const getFavoriteStatus = async () => {
  if (!localStorage.getItem('token')) return 
  try {
    const res = await checkFavoriteStatus(route.params.id)
    isFavorite.value = res.is_favorite
  } catch (err) {
    console.error('检查收藏状态失败', err)
  }
}

// 点击按钮切换收藏/取消收藏
const handleFavorite = async () => {
  if (!localStorage.getItem('token')) {
    ElMessage.warning('请先登录后再进行操作')
    router.push('/login')
    return
  }

  try {
    const res = await toggleFavorite(product.value.id)
    isFavorite.value = res.is_favorite // 后端返回最新的状态
    if (isFavorite.value) {
      ElMessage.success('已加入收藏夹')
    } else {
      ElMessage.info('已取消收藏')
    }
  } catch (err) {
    console.error('操作收藏失败', err)
  }
}


// 举报逻辑
const reportVisible = ref(false)
const reportLoading = ref(false)
const reportForm = reactive({
  reason: '',
  content: ''
})

// 提交举报
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

   // 获取用户地址列表
  try {
    const res = await getAddresses()
    addressList.value = res.results || res
    
    if (addressList.value.length === 0) {
      // 如果没填过地址，引导去个人中心
      await ElMessageBox.confirm('您还没有设置收货地址，请先去设置', '提示', {
        confirmButtonText: '去设置',
        cancelButtonText: '取消',
        type: 'info'
      })
      router.push('/user/profile')
      return
    }

    // 默认选中那个标为“默认”的地址
    const defaultAddr = addressList.value.find(a => a.is_default)
    selectedAddressId.value = defaultAddr ? defaultAddr.id : addressList.value[0].id
    
    // 打开地址选择弹窗
    addressVisible.value = true
  } catch (err) {
    console.error('获取地址失败', err)
  }
}

// 添加到购物车
const handleAddToCart = async () => {
  // 1. 登录校验
  if (!localStorage.getItem('token')) {
    ElMessage.warning('请先登录后再操作')
    router.push('/login')
    return
  }

  // 2. 权限校验：不能把自己的商品加进购物车
  // 注意：product.value.owner 是卖家ID
  // 如果需要严格校验，可以从 getProfile 拿到当前用户ID对比
  
  try {
    await addToCart({ product: product.value.id })
    
    // 🚀 企业级交互：成功的正向反馈
    ElMessage({
      message: '已成功加入购物车！',
      type: 'success',
      duration: 2000,
      showClose: true
    })
  } catch (err) {
    // 拦截器会处理“商品已在购物车中”等后端返回的错误
    console.error(err)
  }
}

// 3. 核心：最终确认下单函数
const confirmOrder = async () => {
  const chosenAddress = addressList.value.find(a => a.id === selectedAddressId.value)
  if (!chosenAddress) return // 安全校验
  orderLoading.value = true
  try {
    const orderData = {
      product_id: product.value.id,
      address: {
        receiver: chosenAddress.receiver,
        mobile: chosenAddress.mobile,
        region: chosenAddress.region,
        detail: chosenAddress.detail
      }
    }

    // 🚀 【关键修改点 1】：接收后端返回的订单对象
    // 后端接口执行成功后，通常会把新生成的订单数据发回来，其中包含订单的数据库 ID
    const res = await createOrder(orderData)
    
    ElMessage.success('订单已提交，正在前往收银台...')
    
    // 关闭地址选择弹窗
    addressVisible.value = false
    
    // 🚀 【关键修改点 2】：跳转到支付收银台，并带上订单 ID
    // 这里的 res.id 是后端返回的订单主键
    router.push(`/payment/${res.id}`)

  } catch (err) {
    console.error('下单过程出错:', err)
    // 拦截器会自动处理报错提示
  } finally {
    orderLoading.value = false
  }
}


onMounted(async () => {
  const id = route.params.id
  const res = await getProductDetail(id)
  product.value = res
  isFavorite.value = res.is_favorited
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