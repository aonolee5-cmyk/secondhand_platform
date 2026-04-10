<template>
  <div class="home-container">
    <!-- 1. 顶部筛选面板 (企业级规范) -->
    <el-card class="filter-panel" shadow="never">
      <!-- 分类筛选 -->
      <div class="filter-group">
        <span class="label">分类：</span>
        <div class="tags">
          <el-check-tag
            :checked="!filterForm.category"
            @change="handleCategoryChange(null)"
            class="tag-item"
          >全部</el-check-tag>
          <el-check-tag
            v-for="cat in categories"
            :key="cat.id"
            :checked="filterForm.category === cat.id"
            @change="handleCategoryChange(cat.id)"
            class="tag-item"
          >{{ cat.name }}</el-check-tag>
        </div>
      </div>

      <el-divider border-style="dashed" />

      <!-- 价格与排序筛选 -->
      <div class="filter-row">
        <div class="filter-group">
          <span class="label">价格：</span>
          <el-input-number v-model="filterForm.min_price" size="small" :controls="false" placeholder="最低价" class="price-input" />
          <span class="split">-</span>
          <el-input-number v-model="filterForm.max_price" size="small" :controls="false" placeholder="最高价" class="price-input" />
          <el-button type="primary" size="small" @click="loadProducts" style="margin-left: 12px">确定</el-button>
        </div>

        <div class="filter-group" style="margin-left: 40px">
          <span class="label">排序：</span>
          <el-select v-model="filterForm.ordering" size="small" @change="loadProducts" style="width: 120px">
            <el-option label="最新发布" value="-create_time" />
            <el-option label="价格从低到高" value="price" />
            <el-option label="价格从高到低" value="-price" />
          </el-select>
        </div>

        <el-button size="small" plain @click="resetFilters" style="margin-left: auto">重置</el-button>
      </div>
    </el-card>

    <!-- 2. 商品瀑布流列表 -->
    <el-row :gutter="20" v-loading="loading" class="product-grid">
      <el-col :xs="12" :sm="8" :md="6" :lg="6" v-for="item in productList" :key="item.id">
        <el-card class="product-card" :body-style="{ padding: '0px' }" @click="$router.push(`/product/${item.id}`)">
          <div class="image-wrapper">
            <el-image 
              :src="item.images[0] ? 'http://127.0.0.1:8000' + item.images[0] : 'https://via.placeholder.com/150'" 
              fit="cover" 
              class="image"
            />
          </div>
          <div class="info">
            <div class="title">{{ item.title }}</div>
            <div class="bottom">
              <span class="price">￥{{ item.price }}</span>
              <span class="owner">{{ item.owner_name }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 3. 空状态提示 -->
    <el-empty v-if="!loading && productList.length === 0" description="没有找到相关的宝贝哦" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getCategories, searchProducts } from '@/api/goods'

const route = useRoute()
const loading = ref(false)
const categories = ref([])
const productList = ref([])

// 🚀 统一筛选状态管理
const filterForm = reactive({
  category: null,
  min_price: null,
  max_price: null,
  ordering: '-create_time'
})

// 加载分类数据
const fetchCategories = async () => {
  categories.value = await getCategories()
}

// 🚀 唯一核心加载函数
const loadProducts = async () => {
  loading.value = true
  const params = {
    status: 'onsale', // 强制只看在售
    search: route.query.q, // 顶部导航栏传来的搜索词
    category: filterForm.category,
    price__gte: filterForm.min_price,
    price__lte: filterForm.max_price,
    ordering: filterForm.ordering
  }
  
  try {
    const res = await searchProducts(params)
    productList.value = res.results || res
  } catch (error) {
    console.error('加载商品失败', error)
  } finally {
    loading.value = false
  }
}

// 处理分类切换
const handleCategoryChange = (id) => {
  filterForm.category = id
  loadProducts()
}

// 重置筛选
const resetFilters = () => {
  filterForm.category = null
  filterForm.min_price = null
  filterForm.max_price = null
  filterForm.ordering = '-create_time'
  loadProducts()
}

// 监听顶部导航栏发起的搜索变化
watch(() => route.query.q, () => {
  loadProducts()
})

onMounted(() => {
  fetchCategories()
  loadProducts()
})
</script>

<style scoped lang="scss">
.home-container {
  padding: 20px 0;
}

.filter-panel {
  margin-bottom: 25px;
  border-radius: 8px;
  .filter-group {
    display: flex;
    align-items: center;
    .label { font-size: 14px; color: #909399; width: 60px; }
    .tags { flex: 1; }
    .tag-item { margin-right: 8px; cursor: pointer; }
  }
  .filter-row {
    display: flex;
    align-items: center;
    .price-input { width: 90px; }
    .split { margin: 0 8px; color: #dcdfe6; }
  }
}

.product-grid {
  min-height: 400px;
}

.product-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  }
  
  .image-wrapper {
    height: 200px;
    overflow: hidden;
    .image { width: 100%; height: 100%; }
  }

  .info {
    padding: 12px;
    .title {
      font-size: 14px;
      font-weight: bold;
      height: 40px;
      overflow: hidden;
      margin-bottom: 10px;
      line-height: 20px;
    }
    .bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;
      .price { color: #f56c6c; font-size: 18px; font-weight: 600; }
      .owner { font-size: 12px; color: #909399; }
    }
  }
}

.el-divider {
  margin: 15px 0;
}
</style>