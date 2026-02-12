<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <div class="logo">二手交易平台</div>
        <div class="user-info">
          <el-button type="primary" @click="$router.push('/post')">发布闲置</el-button>
        </div>
      </el-header>
      
      <el-main>
        <el-row :gutter="20">
          <el-col :span="6" v-for="item in productList" :key="item.id">
            <el-card class="product-card" @click="$router.push(`/goods/${item.id}`)">
              <!-- 这里处理图片 URL，如果后端传的是相对路径，需要拼上基准地址 -->
              <img :src="item.images[0] ? 'http://127.0.0.1:8000' + item.images[0] : 'https://via.placeholder.com/150'" class="image" />
              <div style="padding: 14px">
                <div class="title">{{ item.title }}</div>
                <div class="bottom">
                  <span class="price">￥{{ item.price }}</span>
                  <el-button text class="button">查看详情</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { useRoute } from 'vue-router'
import { searchProducts } from '@/api/goods'
import { watch } from 'vue'

const route = useRoute()
const productList = ref([])

onMounted(async () => {
  // 我们直接调用列表接口获取所有“在售”商品
  const res = await request({ url: '/goods/products/', method: 'get' })
  // 注意：因为我们后端逻辑里，发布后默认是 audit (审核中)
  // 你需要在后台手动把商品的 status 改成 onsale，首页才能看到
  productList.value = res.results || res 
})

// 
const fetchProducts = async () => {
  const params = {
    search: route.query.q, // 获取 URL 里的搜索词
    category: route.query.cat
  }
  try {
    const res = await searchProducts(params)
    // 这种写法兼容性最强：
    productList.value = Array.isArray(res) ? res : (res.results || [])
  } catch (error) {
    console.error("加载商品失败", error)
  }
}

const loadProducts = async () => {
  const params = {}
  if (route.query.q) params.search = route.query.q
  if (route.query.cat) params.category = route.query.cat
  
  // 强制指定只看在售的
  params.status = 'onsale'

  console.log('--- 准备请求后端 ---', params)
  
  try {
    const res = await searchProducts(params)
    productList.value = Array.isArray(res) ? res : (res.results || [])
  } catch (error) {
    console.error('加载失败', error)
  }
}


watch(
  () => route.query,
  () => {
    console.log('路由参数变化了', route.query)
    loadProducts()
  },
  { deep: true } // 深度监听
)

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; }
.logo { font-size: 20px; font-weight: bold; color: #409eff; }
.product-card { margin-bottom: 20px; }
.image { width: 100%; height: 200px; object-fit: cover; display: block; }
.title { font-weight: bold; margin-bottom: 10px; height: 40px; overflow: hidden; }
.price { color: #f56c6c; font-size: 18px; }
</style>