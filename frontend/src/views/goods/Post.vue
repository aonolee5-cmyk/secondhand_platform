<template>
  <div class="post-container">
    <el-card :header="isEdit ? '修改宝贝信息' : '发布闲置物品'">
      <el-form :model="form" label-width="120px" v-loading="loading">
        <!-- 1. 基础信息 -->
        <el-form-item label="商品名称" required>
          <el-input v-model="form.title" placeholder="请输入商品名" />
        </el-form-item>
        
        <el-form-item label="所属分类" required>
          <el-select 
            v-model="form.category" 
            placeholder="请选择"
            @change="handleCategoryChange"
            style="width: 100%"
          >
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        

        <div v-if="dynamicFields.length > 0" class="dynamic-attr-wrapper">
          <el-divider content-position="left">
            <el-icon><Setting /></el-icon> 规格参数 ({{ selectedCatName }})
          </el-divider>
          
          <el-row :gutter="20">
            <el-col :span="12" v-for="field in dynamicFields" :key="field">
              <el-form-item :label="field">
                <el-input v-model="form.attributes[field]" :placeholder="'请输入' + field" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>


        <div class="custom-attr-section">
          <el-divider content-position="left">更多补充信息</el-divider>
          <div v-for="(attr, index) in customAttrs" :key="index" class="custom-attr-row" style="display:flex; gap:10px; margin-bottom:10px; margin-left:40px">
            <el-input v-model="attr.k" placeholder="参数名" style="width: 150px" />
            <span class="split">:</span>
            <el-input v-model="attr.v" placeholder="参数值" style="flex: 1" />
            <el-button type="danger" icon="Delete" circle @click="removeCustomAttr(index)" />
          </div>
          <el-button type="primary" link icon="Plus" @click="addCustomAttr" style="margin-left: 40px">
            增加自定义规格
          </el-button>
        </div>

        <el-form-item label="价格" style="margin-top: 20px" required>
          <el-input-number v-model="form.price" :precision="2" :step="0.1" :min="0" />
        </el-form-item>

        <el-form-item label="物品图片" required>
          <el-upload
            action="/api/goods/list/upload_image/"
            list-type="picture-card"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :file-list="fileList"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item label="详细描述">
          <el-input v-model="form.desc" type="textarea" :rows="4" placeholder="描述一下你的宝贝吧" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="submitting" size="large">
            {{ isEdit ? '保存修改' : '确认发布' }}
          </el-button>
          <el-button @click="$router.go(-1)" size="large">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCategories, postProduct, getProductDetail, updateProduct } from '@/api/goods'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const categories = ref([])
const loading = ref(false)
const submitting = ref(false)
const fileList = ref([])

const dynamicFields = ref([]) 
const selectedCatName = ref('')
const customAttrs = ref([])

const form = reactive({
  title: '',
  category: '',
  price: 0,
  desc: '',
  images: [],
  attributes: {} 
})

const isEdit = computed(() => !!route.params.id)
const uploadHeaders = { Authorization: `Bearer ${localStorage.getItem('token')}` }


const handleCategoryChange = (val) => {
  const cat = categories.value.find(item => item.id === val)
  if (!cat) return

  selectedCatName.value = cat.name
  dynamicFields.value = cat.attribute_fields || []
  const newAttrs = {}
  dynamicFields.value.forEach(field => {
    newAttrs[field] = form.attributes[field] || ''
  })
  form.attributes = newAttrs
}

const addCustomAttr = () => { customAttrs.value.push({ k: '', v: '' }) }
const removeCustomAttr = (index) => { customAttrs.value.splice(index, 1) }

const handleUploadSuccess = (res) => { 
  form.images.push(res.url) 
}

onMounted(async () => {
  // 加载全部分类
  const res = await getCategories()
  categories.value = res.results || res

  if (isEdit.value) {
    loading.value = true
    try {
      const detail = await getProductDetail(route.params.id)
      Object.assign(form, {
        title: detail.title,
        category: detail.category,
        price: parseFloat(detail.price),
        desc: detail.desc,
        images: detail.images || [],
        attributes: detail.attributes || {}
      })
      handleCategoryChange(detail.category)
    } finally {
      loading.value = false
    }
  }
})

const onSubmit = async () => {
  const finalAttributes = { ...form.attributes }
  customAttrs.value.forEach(item => {
    if (item.k.trim() && item.v.trim()) {
      finalAttributes[item.k] = item.v
    }
  })
  
  // 更新 form 对象
  form.attributes = finalAttributes

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateProduct(route.params.id, form)
      ElMessage.success('信息已更新')
    } else {
      await postProduct(form)
      ElMessage.success('宝贝发布成功，请等待审核')
    }
    router.push('/user/products') // 跳回我的发布列表
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.post-container { max-width: 800px; margin: 20px auto; }
.preview-img { width: 100px; height: 100px; margin-right: 10px; border-radius: 8px; }
.img-preview-list { margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 10px; }
.custom-attr-row { align-items: center; .split { color: #999; } }
</style>