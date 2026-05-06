<template>
  <div class="cart-page-wrapper">
    <div class="cart-container">
      <el-card header="我的购物车">
        <el-table :data="cartList">
          <el-table-column label="商品" width="400">
            <template #default="scope">
              <div class="product-item">
                <el-image :src="'http://127.0.0.1:8000'+scope.row.product_image" style="width: 60px" />
                <span style="margin-left: 10px">{{ scope.row.product_title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="product_price" label="单价" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="danger" @click="handleDelete(scope.row.id)">移除</el-button>
              <el-button type="primary" @click="goToCheckout(scope.row)">立即下单</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  <el-dialog v-model="addressVisible" title="确认收货信息" width="500px">
    <div class="address-selector">
      <el-radio-group v-model="selectedAddressId" style="width: 100%">
        <el-card 
          v-for="addr in addressList" 
          :key="addr.id" 
          :class="['addr-card', { active: selectedAddressId === addr.id }]"
          shadow="never"
          @click="selectedAddressId = addr.id"
          style="margin-bottom: 10px; cursor: pointer"
        >
          <el-radio :label="addr.id">
            <div class="addr-info">
              <span style="font-weight: bold">{{ addr.receiver }}</span>
              <span style="margin-left: 10px; color: #666">{{ addr.mobile }}</span>
              <p style="margin: 5px 0 0; font-size: 13px; color: #999">
                {{ addr.region }} {{ addr.detail }}
              </p>
            </div>
          </el-radio>
        </el-card>
      </el-radio-group>
    </div>
    <template #footer>
      <el-button @click="addressVisible = false">返回</el-button>
      <el-button type="danger" @click="confirmOrder">确认下单并去支付</el-button>
    </template>
  </el-dialog>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { getAddresses } from '@/api/user' 
import { createOrder } from '@/api/trade'

const router = useRouter()
const cartList = ref([])

// 地址相关状态
const addressVisible = ref(false)
const addressList = ref([])
const selectedAddressId = ref(null)
const currentOrderProduct = ref(null) 

// 加载购物车数据
const loadCart = async () => {
  try {
    const res = await request({ url: '/trade/cart/', method: 'get' })
    cartList.value = res.results || res
  } catch (error) {
    console.error('加载购物车失败:', error)
  }
}

// 立即下单逻辑：准备阶段
const goToCheckout = async (item) => {
  currentOrderProduct.value = item
  try {
    const res = await getAddresses()
    addressList.value = res.results || res.data?.results || res

    if (addressList.value.length === 0) {
      ElMessage.warning('请先设置收货地址')
      router.push('/user/profile')
      return
    }

    // 默认选中
    const defaultAddr = addressList.value.find(a => a.is_default)
    selectedAddressId.value = defaultAddr ? defaultAddr.id : addressList.value[0].id
    addressVisible.value = true
  } catch (err) {
    console.error('获取地址失败:', err)
  }
}

// 核心：确认下单并执行跳转
const confirmOrder = async () => {
  const chosenAddress = addressList.value.find(a => a.id === selectedAddressId.value)
  
  try {
    const orderData = {
      product_id: currentOrderProduct.value.product, 
      address: {
        receiver: chosenAddress.receiver,
        mobile: chosenAddress.mobile,
        region: chosenAddress.region,
        detail: chosenAddress.detail
      }
    }

    // 调用后端下单接口
    const res = await createOrder(orderData)
    
    console.log('下单接口返回全量数据:', res)

    // 兼容多种数据结构获取 ID
    const orderId = res.id || (res.data && res.data.id)

    if (orderId) {
      ElMessage.success('订单已创建，转向支付页...')
      addressVisible.value = false
      router.push(`/payment/${orderId}`) 
    } else {
      ElMessage.warning('下单成功，请在订单中心支付')
      router.push('/orders')
    }
  } catch (err) {
    console.error('下单失败:', err)
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要从购物车移除吗？', '提示', { type: 'warning' })
    await request({ url: `/trade/cart/${id}/`, method: 'delete' })
    ElMessage.success('已移除')
    loadCart()
  } catch (err) { /* 取消则不操作 */ }
}


onMounted(() => {
  loadCart()
})
</script>

<style scoped>
.product-item { display: flex; align-items: center; }
.cart-container { padding: 20px; }
</style>