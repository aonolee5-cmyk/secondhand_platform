<template>
  <div class="my-products">
    <el-page-header @back="$router.go(-1)" content="我发布的商品" />
    
    <el-table :data="myProducts" style="width: 100%; margin-top: 20px" stripe>
      <el-table-column label="图片" width="120">
        <template #default="scope">
          <el-image 
            :src="scope.row.images[0]?.startsWith('http') ? scope.row.images[0] : 'http://127.0.0.1:8000' + scope.row.images[0]" 
            style="width: 80px; height: 80px; border-radius: 4px;" 
            fit="cover"
          />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="商品标题" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="scope">
          <span style="color: #f56c6c; font-weight: bold;">￥{{ scope.row.price }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="状态" width="120">
        <template #default="scope">
          <el-tag :type="statusMap[scope.row.status]?.type">
            {{ statusMap[scope.row.status]?.text }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="260"> 
        <template #default="scope">
          
          <!-- 🚀 场景 1：被违规封禁 -->
          <div v-if="scope.row.status === 'banned'">
             <el-tag type="danger" effect="dark" style="margin-right: 10px">违规封禁</el-tag>
             <el-button size="small" type="primary" @click="$router.push('/edit/' + scope.row.id)">修改申诉</el-button>
          </div>

          <!-- 🚀 场景 2：正在审核中 (体现企业级逻辑：只读，允许撤回) -->
          <div v-else-if="scope.row.status === 'audit'">
            <el-button-group>
              <el-button size="small" type="info" plain @click="$router.push('/product/' + scope.row.id)">预览</el-button>
              <el-button size="small" type="warning" @click="handleStatus(scope.row, 'off')">撤回审核</el-button>
            </el-button-group>
            <p style="font-size: 12px; color: #999; margin: 5px 0 0">审核期间不可修改信息</p>
          </div>

          <!-- 🚀 场景 3：已售出 或 交易锁定 -->
          <div v-else-if="['locked', 'sold'].includes(scope.row.status)">
            <el-button size="small" type="info" plain @click="$router.push('/order-detail/' + scope.row.id)">查看交易</el-button>
          </div>

          <!-- 🚀 场景 4：正常状态 (在售 或 用户主动下架) -->
          <div v-else>
            <el-button-group>
              <!-- 在售显示下架 -->
              <el-button 
                v-if="scope.row.status === 'onsale'" 
                size="small" 
                type="danger" 
                @click="handleStatus(scope.row, 'off')"
              >下架</el-button>
              
              <!-- 下架显示上架 (点击后进入 audit) -->
              <el-button 
                v-if="scope.row.status === 'off'" 
                size="small" 
                type="success" 
                @click="handleStatus(scope.row, 'onsale')"
              >重新上架</el-button>

              <el-button 
                size="small" 
                type="primary" 
                @click="$router.push('/edit/' + scope.row.id)"
              >编辑</el-button>
            </el-button-group>
          </div>

        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router' 
import { getMyProducts, updateProductStatus } from '@/api/goods'
import { ElMessage } from 'element-plus'

const router = useRouter() 
const myProducts = ref([])

// 🚀 完善状态映射表，加入 banned
const statusMap = {
  'audit': { text: '审核中', type: 'info' },
  'onsale': { text: '在售中', type: 'success' },
  'locked': { text: '交易中', type: 'warning'},
  'sold': { text: '已售出', type: 'warning' },
  'off': { text: '已下架', type: 'danger' },
  'banned': { text: '违规禁售', type: 'danger' }
}

const loadMyData = async () => {
  const res = await getMyProducts()
  // 确保数据渲染正常
  myProducts.value = res.results || res || []
}

const handleStatus = async (row, status) => {
  try {
    await updateProductStatus(row.id, status)
    if (status === 'onsale') {
      ElMessage.success('已提交重新审核')
    } else if (status === 'off' && row.status === 'audit') {
      ElMessage.info('已撤回审核申请')
    } else {
      ElMessage.success('操作成功')
    }
    loadMyData()
  } catch (err) {
    console.error(err)
  }
}

onMounted(loadMyData)
</script>