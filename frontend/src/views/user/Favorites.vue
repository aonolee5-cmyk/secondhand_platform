<template>
  <div class="favorites-container">
    <div class="page-header">
      <h3 class="title">我的收藏 ({{ favoriteList.length }})</h3>
    </div>

    <!-- 📦 收藏列表 -->
    <el-row :gutter="20" v-if="favoriteList.length > 0">
      <el-col :span="6" v-for="item in favoriteList" :key="item.id">
        <el-card class="fav-card" :body-style="{ padding: '0px' }">
          <div class="image-box" @click="$router.push('/product/' + item.product)">
            <el-image 
              :src="'http://127.0.0.1:8000' + item.product_details.images[0]" 
              fit="cover" 
              class="prod-img" 
            />
          </div>
          
          <div class="info-box">
            <h4 class="prod-title">{{ item.product_details.title }}</h4>
            <div class="bottom-row">
              <span class="price">￥{{ item.product_details.price }}</span>
              <el-button 
                type="danger" 
                icon="Delete" 
                circle 
                size="small" 
                plain
                @click="handleRemove(item.id)" 
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 🏜️ 空状态 -->
    <el-empty v-else description="还没有收藏任何宝贝哦，去首页逛逛吧" :image-size="200">
      <el-button type="primary" round @click="$router.push('/')">去逛逛</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'

const favoriteList = ref([])

const loadFavorites = async () => {
  const res = await request({ url: '/trade/favorites/', method: 'get' })
  favoriteList.value = res.results || res
}

const handleRemove = (id) => {
  ElMessageBox.confirm('确定要取消收藏该商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await request({ url: `/trade/favorites/${id}/`, method: 'delete' })
    ElMessage.success('已取消收藏')
    loadFavorites()
  })
}

onMounted(loadFavorites)
</script>

<style scoped lang="scss">
.favorites-container {
  padding: 20px;
  
  .page-header {
    margin-bottom: 25px;
    .title { font-size: 18px; font-weight: 600; color: #333; }
  }

  .fav-card {
    margin-bottom: 20px;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s;
    &:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1) !important; }

    .image-box {
      height: 160px;
      cursor: pointer;
      .prod-img { width: 100%; height: 100%; }
    }

    .info-box {
      padding: 12px;
      .prod-title {
        font-size: 14px;
        margin: 0 0 10px;
        height: 40px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }
      .bottom-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        .price { color: #f56c6c; font-size: 16px; font-weight: bold; }
      }
    }
  }
}
</style>