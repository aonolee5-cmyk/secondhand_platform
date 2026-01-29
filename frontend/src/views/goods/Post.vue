<template>
  <div class="post-container">
    <el-card header="发布闲置物品">
      <el-form :model="form" label-width="100px">
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
          <el-upload
            action="/api/goods/products/upload_image/"
            list-type="picture-card"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="详细描述">
          <el-input v-model="form.desc" type="textarea" rows="4" placeholder="说说你的宝贝是从哪买的，成色如何..." />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSubmit">确认发布</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getCategories, postProduct } from '@/api/goods'
import { ElMessage } from 'element-plus'

const categories = ref([])
const form = reactive({
  title: '',
  category: '',
  price: 0,
  desc: '',
  images: [],
  attributes: {}
})

// 上传图片需要带 Token
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

onMounted(async () => {
  const res = await getCategories()
  categories.value = res
})

const handleUploadSuccess = (res) => {
  form.images.push(res.url)
}

const onSubmit = async () => {
  try {
    await postProduct(form)
    ElMessage.success('发布成功，请等待审核！')
  } catch (err) {
    console.error(err)
  }
}
</script>