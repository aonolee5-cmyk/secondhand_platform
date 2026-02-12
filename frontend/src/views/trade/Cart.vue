<template>
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
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const cartList = ref([]) // 对应模板中的 :data="cartList"

// 加载购物车数据
const loadCart = async () => {
  try {
    const res = await request({ url: '/trade/cart/', method: 'get' })
    cartList.value = res.results || res
  } catch (error) {
    console.error(error)
  }
}

onMounted(loadCart)

// 移除商品逻辑
const handleDelete = async (id) => {
  await ElMessageBox.confirm('确定要从购物车移除该商品吗？', '提示')
  await request({ url: `/trade/cart/${id}/`, method: 'delete' })
  ElMessage.success('已移除')
  loadCart()
}

// 立即下单逻辑
const goToCheckout = (row) => {
  // 跳转到确认订单页，带上商品ID
  router.push({
    path: '/checkout',
    query: { product_id: row.product }
  })
}
</script>

<style scoped>
.product-item { display: flex; align-items: center; }
.cart-container { padding: 20px; }
</style>