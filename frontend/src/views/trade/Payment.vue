<template>
  <div class="alipay-simulator">
    <el-card class="alipay-card">
      <div class="alipay-header">
        <span class="ali-text">安全支付</span>
      </div>

      <div class="pay-main-content"> 
        <div class="order-brief">
          <p class="desc">正在向 <strong>{{ orderInfo.seller_name || '获取中...' }}</strong> 发起付款</p>
          <div class="amount-box">
            <span class="unit">￥</span>
            <span class="num">{{ orderInfo.total_amount }}</span>
          </div>
          <p class="sn">订单号：{{ orderInfo.order_sn }}</p>
        </div>

        <el-divider>请使用支付宝扫码支付</el-divider>

        <div class="qr-container" v-loading="paying">
          <div class="qr-box">
             <el-image 
               src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=SecondHandPlatformPay" 
               class="qr-code"
             />
             <div v-if="paySuccess" class="qr-mask">
                <el-icon color="#67C23A" :size="60"><CircleCheckFilled /></el-icon>
                <p>支付成功</p>
             </div>
          </div>
          <p class="qr-tip">打开手机支付宝 [扫一扫]</p>
        </div>

        <div class="actions">
          <el-button 
            type="primary" 
            size="large" 
            class="full-btn" 
            @click="simulatePayment" 
            :disabled="paySuccess"
          >
            {{ paying ? '正在与银行中心通信...' : '确认付款' }}
          </el-button>


          <el-link 
            type="info" 
            @click="$router.push('/user/orders')" 
            style="margin-top: 15px"
          >
            返回订单中心
          </el-link>
        </div>
      </div> 
    </el-card>

    <!-- 支付中的全屏 Loading -->
    <div v-if="showProcessing" class="processing-overlay">
       <el-icon class="is-loading" :size="40" color="#fff"><Loading /></el-icon>
       <p>正在拉取支付宝安全验证...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { CircleCheckFilled, Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const orderInfo = ref({})
const paying = ref(false)
const paySuccess = ref(false)
const showProcessing = ref(true)

// 初始化页面
onMounted(async () => {
  setTimeout(async () => {
    try {
      const res = await request({ url: `/trade/orders/${route.params.id}/`, method: 'get' })
      orderInfo.value = res
      showProcessing.value = false
    } catch (err) {
      router.push('/orders')
    }
  }, 800) 
})

// 模拟支付
const simulatePayment = async () => {
  paying.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  try {
    await request({ url: `/trade/orders/${route.params.id}/pay/`, method: 'post' })
    

    paySuccess.value = true
    ElMessage.success('支付宝扣款成功')
    

    setTimeout(() => {
      router.push({
        path: '/pay-success',
        query: { id: route.params.id }
      })
    }, 1500)

  } catch (err) {
    paying.value = false
  }
}
</script>

<style scoped lang="scss">
.alipay-simulator {
  min-height: 90vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  padding: 20px;
}

.alipay-card {
  width: 450px;
  border-radius: 4px;
  border-top: 4px solid #00a0e9; 
  .alipay-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f0f0f0;
    .ali-text { font-size: 14px; color: #999; }
  }
}

.order-brief {
  text-align: center;
  padding: 30px 0;
  .desc { color: #666; margin-bottom: 10px; }
  .amount-box {
    color: #333;
    margin-bottom: 10px;
    .unit { font-size: 20px; font-weight: bold; }
    .num { font-size: 42px; font-weight: bold; }
  }
  .sn { font-size: 12px; color: #999; }
}

.qr-container {
  text-align: center;
  padding: 20px 0;
  .qr-box {
    position: relative;
    width: 200px;
    height: 200px;
    margin: 0 auto;
    border: 1px solid #eee;
    padding: 10px;
    .qr-mask {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(255,255,255,0.9);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      p { font-weight: bold; color: #67C23A; margin-top: 10px; }
    }
  }
  .qr-tip { margin-top: 15px; color: #666; font-size: 14px; }
}

.actions {
  padding: 20px 0;
  text-align: center;
  .full-btn { width: 100%; height: 50px; font-size: 18px; }
}

.processing-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.7); z-index: 2000;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #fff; p { margin-top: 20px; }
}
</style>