<template>
  <div class="post-container">
    <!-- 标题根据模式动态显示 -->
    <el-card :header="isEdit ? '修改宝贝信息' : '发布闲置物品'">
      <el-form :model="form" label-width="100px" v-loading="loading">
        <el-form-item label="商品名称">
          <el-input v-model="form.title" placeholder="品牌 品类 核心参数" />
        </el-form-item>
        
        <el-form-item label="所属分类">
          <el-select 
            v-model="form.category" 
            placeholder="请选择"
            @change="handleCategoryChange"
          >
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        
        <div v-if="dynamicFields.length > 0" class="dynamic-attr-wrapper">
          <!-- 用分割线美化，显示当前分类名称 -->
          <el-divider content-position="left">规格参数 ({{ selectedCatName }})</el-divider>
          
          <!-- 循环渲染后端 Category 传过来的 attribute_fields 数组 -->
          <el-form-item 
            v-for="field in dynamicFields" 
            :key="field" 
            :label="field"
          >
            <!-- 🚀 核心：双向绑定到 form.attributes 这个 JSON 对象里 -->
            <el-input 
              v-model="form.attributes[field]" 
              :placeholder="'请输入' + field" 
            />
          </el-form-item>
        </div>

        <el-form-item label="价格">
          <el-input-number v-model="form.price" :precision="2" :step="0.1" :min="0" />
        </el-form-item>

        <el-form-item label="物品图片">
          <!-- 如果是编辑模式，显示已经上传过的图片预览 -->
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
          <!-- 按钮文字动态切换 -->
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
const dynamicFields = ref([]) // 动态参数字段
const selectedCatName = ref('') // 当前选中的分类名称

// 通过url里有没有id来判断是发布还是编辑
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


// 处理分类选择
const handleCategoryChange = (val) => {
  // 从加载好的 categories 列表中找到选中的那一个
  const cat = categories.value.find(item => item.id === val)
  if (cat) {
    selectedCatName.value = cat.name
    // 获取后端配置的 attribute_fields (我们在 Category 模型里加的字段)
    dynamicFields.value = cat.attribute_fields || []
    
    // 🚀 初始化属性对象：确保 form.attributes 里有这些键，防止报错
    // 如果是“发布模式”，我们清空旧属性；如果是“编辑模式”，则保留已有值
    if (!isEdit.value) {
      form.attributes = {}
      dynamicFields.value.forEach(f => {
        form.attributes[f] = '' // 预设为空字符串
      })
    } else {
      // 编辑模式下，如果新选的分类有字段在原属性里没有，补齐它
      dynamicFields.value.forEach(f => {
        if (!(f in form.attributes)) {
          form.attributes[f] = ''
        }
      })
    }
  }
}

onMounted(async () => {
  const catRes = await getCategories()
  categories.value = catRes

  if (isEdit.value) {
    loading.value = true
    try {
      const detail = await getProductDetail(route.params.id)
      Object.assign(form, {
        title: detail.title,
        category: detail.category,
        price: parseFloat(detail.price),
        desc: detail.desc,
        images: detail.images,
        attributes: detail.attributes || {} // 🚀 确保是对象
      })
      // 🚀 重点：手动触发一次切换逻辑，让编辑页进来时立刻显示出那些动态输入框
      handleCategoryChange(detail.category)
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
    // 根据模式调用不同的api
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