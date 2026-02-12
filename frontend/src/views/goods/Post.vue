<template>
  <div class="post-container">
    <!-- 修改点 1：标题根据模式动态显示 -->
    <el-card :header="isEdit ? '修改宝贝信息' : '发布闲置物品'">
      <el-form :model="form" label-width="100px" v-loading="loading">
        <el-form-item label="商品名称">
          <el-input v-model="form.title" placeholder="品牌 品类 核心参数" />
        </el-form-item>
        
        <el-form-item label="所属分类">
          <el-select v-model="form.category" placeholder="请选择">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="价格">
          <el-input-number v-model="form.price" :precision="2" :step="0.1" :min="0" />
        </el-form-item>

        <el-form-item label="物品图片">
          <!-- 修改点 2：如果是编辑模式，显示已经上传过的图片预览 -->
          <div v-if="form.images.length > 0" style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 10px;">
            <el-image 
              v-for="(url, index) in form.images" 
              :key="index" 
              :src="'http://127.0.0.1:8000' + url" 
              style="width: 100px; height: 100px; border-radius: 4px;"
              fit="cover"
            />
          </div>
          <el-upload
            action="/api/goods/list/upload_image/"
            list-type="picture-card"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="详细描述">
          <el-input v-model="form.desc" type="textarea" :rows="4" placeholder="说说你的宝贝是从哪买的，成色如何..." />
        </el-form-item>

        <el-form-item>
          <!-- 修改点 3：按钮文字动态切换 -->
          <el-button type="primary" @click="onSubmit" :loading="submitting">
            {{ isEdit ? '保存修改' : '确认发布' }}
          </el-button>
          <el-button @click="$router.go(-1)">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router' // 引入路由工具
import { getCategories, postProduct, getProductDetail, updateProduct } from '@/api/goods' // 引入 API
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const categories = ref([])
const loading = ref(false)     // 用于加载旧数据时的转圈提示
const submitting = ref(false)  // 防止重复点击提交

// 修改点 4：核心逻辑判断，通过 URL 里有没有 id 来判断是“发布”还是“编辑”
const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  category: '',
  price: 0,
  desc: '',
  images: [],
  attributes: {}
})

const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

onMounted(async () => {
  // 1. 获取分类列表（无论哪种模式都要加载）
  const res = await getCategories()
  categories.value = res

  // 修改点 5：如果是编辑模式，根据 ID 去后端拿旧数据回显到表单里
  if (isEdit.value) {
    loading.value = true
    try {
      const detail = await getProductDetail(route.params.id)
      // 把旧数据填进表单
      form.title = detail.title
      form.category = detail.category
      form.price = parseFloat(detail.price)
      form.desc = detail.desc
      form.images = detail.images
      form.attributes = detail.attributes
    } catch (err) {
      console.error('获取详情失败', err)
    } finally {
      loading.value = false
    }
  }
})

const handleUploadSuccess = (res) => {
  form.images.push(res.url)
}

const onSubmit = async () => {
  submitting.value = true
  try {
    // 修改点 6：根据模式调用不同的 API
    if (isEdit.value) {
      await updateProduct(route.params.id, form)
      ElMessage.success('修改成功，已重新进入审核！')
    } else {
      await postProduct(form)
      ElMessage.success('发布成功，请等待审核！')
    }
    router.push('/my-products') // 成功后跳转回我的发布列表
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>