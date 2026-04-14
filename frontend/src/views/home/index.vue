<template>
  <div class="home-container">
    <!-- 1. 顶部筛选面板 (类名已修正为 filter-card) -->
    <el-card class="filter-card" shadow="never">
      <!-- 分类筛选 -->
      <div class="filter-group">
        <span class="label">分类：</span>
        <div class="tags">
          <el-check-tag
            :checked="!filterForm.category"
            @change="handleCategoryChange(null)"
            class="tag-item"
          >
            <el-icon style="vertical-align:middle; margin-right: 4px;">
              <Menu />
            </el-icon>
            全部
          </el-check-tag>
          <el-check-tag
            v-for="cat in categories"
            :key="cat.id"
            :checked="filterForm.category === cat.id"
            @change="handleCategoryChange(cat.id)"
            class="tag-item"
          >
            <el-icon v-if="cat.icon" style="vertical-align:middle; margin-right: 4px;">
              <component :is="cat.icon"/>
            </el-icon>
            {{ cat.name }}
          </el-check-tag>
        </div>
      </div>

      <el-divider border-style="dashed" />

      <!-- 价格与排序筛选 -->
      <div class="filter-row">
        <div class="filter-group">
          <span class="label">价格：</span>
          <el-input-number v-model="filterForm.min_price" size="small" :controls="false" placeholder="最低价" class="price-input" />
          <span class="range-split">-</span>
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

    <!-- 2. 商品瀑布流列表 (类名已修正为 product-item) -->
    <el-row :gutter="20" v-loading="loading" class="product-grid">
      <el-col :xs="12" :sm="8" :md="6" :lg="6" v-for="item in productList" :key="item.id">
        <el-card class="product-item" :body-style="{ padding: '0px' }" @click="$router.push(`/product/${item.id}`)">
          <div class="image-wrapper">
            <el-image 
              :src="item.images[0].startsWith('http') ?  item.images[0] : 'http://127.0.0.1:8000' + item.images[0]"
              fit="cover" 
              class="image"
            />
          </div>
          <div class="info">
            <div class="title">{{ item.title }}</div>
            <div class="product-desc">{{ item.desc }}</div>
            
            <div class="price-row">
              <span class="price">￥{{ item.price }}</span>
              <span class="views">{{ item.browse_count }}人看过</span>
            </div>
            
            <div class="seller-info">
              <el-avatar :size="18" icon="UserFilled" />
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
import { UserFilled,Search, Plus, Shop, ArrowDown, ShoppingCart, Menu } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(false)
const categories = ref([])
const productList = ref([])

const filterForm = reactive({
  category: null,
  min_price: null,
  max_price: null,
  ordering: '-create_time'
})

const fetchCategories = async () => {
  categories.value = await getCategories()
}

const loadProducts = async () => {
  loading.value = true
  const params = {
    status: 'onsale',
    search: route.query.q,
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

const handleCategoryChange = (id) => {
  filterForm.category = id
  loadProducts()
}

const resetFilters = () => {
  filterForm.category = null
  filterForm.min_price = null
  filterForm.max_price = null
  filterForm.ordering = '-create_time'
  loadProducts()
}

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
  background-color: #f5f7fa; 
}

/* 🚀 1. 筛选面板样式 */
.filter-card {
  margin-bottom: 25px;
  border-radius: 12px;
  border: none;
  .filter-group {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    .label { font-size: 14px; color: #909399; width: 60px; font-weight: bold; }
    .tags { flex: 1; display: flex; flex-wrap: wrap; }
    .tag-item { margin-right: 10px; margin-bottom: 5px; cursor: pointer; }
  }
  .filter-row {
    display: flex;
    align-items: center;
    gap: 10px;
    .range-split { color: #dcdfe6; margin: 0 8px; }
    .price-input { width: 100px; }
  }
}

/* 🚀 2. 商品卡片样式 */
.product-item {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: none !important;
  border-radius: 12px !important;
  overflow: hidden;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 15px 30px rgba(0,0,0,0.1) !important;
    .image { transform: scale(1.05); }
  }
  
  .image-wrapper {
    height: 200px;
    overflow: hidden;
    background-color: #f9f9f9;
    .image { 
      width: 100%; 
      height: 100%; 
      transition: transform 0.5s ease;
    }
  }

  .info {
    padding: 15px;
    
    .title { 
      font-size: 16px; 
      font-weight: 700; 
      color: #303133 !important; 
      line-height: 1.4;
      margin-bottom: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .product-desc {
      font-size: 13px;
      color: #606266 !important; 
      line-height: 1.6;
      margin-bottom: 12px;
      height: 42px; 
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      word-break: break-all;
    }

    .price-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 5px;
      .price { 
        color: #f56c6c !important; 
        font-size: 22px; 
        font-weight: 800;
      }
      .views { font-size: 12px; color: #909399; }
    }

    .seller-info {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid #f2f6fc;
      .owner { font-size: 12px; color: #909399 !important; font-weight: 500;}
    }
  }
}

.el-divider { margin: 15px 0; }
</style>