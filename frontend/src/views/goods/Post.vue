<template>
  <div class="post-container">
    <el-card :header="isEdit ? '修改宝贝信息' : '发布闲置物品'">
      <el-form :model="form" label-width="120px" v-loading="loading">
        <!-- 1. 基础信息 -->
        <el-form-item label="商品名称">
          <el-input v-model="form.title" placeholder="品牌 品类 核心参数" />
        </el-form-item>
        
        <el-form-item label="所属分类">
          <el-select 
            v-model="form.category" 
            placeholder="请选择"
            @change="handleCategoryChange"
            style="width: 100%"
          >
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        
        <!-- 🚀 2. 动态规格参数区 (预设模板) -->
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
          <div v-for="(attr, index) in customAttrs" :key="index" class="custom-attr-row">
            <el-input v-model="attr.k" placeholder style="width: 150px" />
            <span class="split">:</span>
            <el-input v-model="attr.v" placeholder style="flex: 1" />
            <el-button type="danger" icon="Delete" circle @click="removeCustomAttr(index)" />
          </div>
          <el-button type="primary" link icon="Plus" @click="addCustomAttr" style="margin-left: 40px">
            增加自定义规格
          </el-button>
        </div>

        <!-- 4. 价格与描述 -->
        <el-form-item label="价格" style="margin-top: 20px">
          <el-input-number v-model="form.price" :precision="2" :step="0.1" :min="0" />
        </el-form-item>

        <el-form-item label="物品图片">
          <div v-if="form.images.length > 0" class="img-preview-list">
            <el-image 
              v-for="(url, index) in form.images" 
              :key="index" 
              :src="url.startsWith('http') ? url : 'http://127.0.0.1:8000' + url" 
              class="preview-img"
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
          <el-input v-model="form.desc" type="textarea" :rows="4" placeholder="说说你的宝贝是从哪买的..." />
        </el-form-item>

        <el-form-item>
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
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCategories, postProduct, getProductDetail, updateProduct } from '@/api/goods'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const categories = ref([])
const loading = ref(false)
const submitting = ref(false)

// 🚀 1. 企业级 12 大分类属性模板库
const categoryTemplates = {
  '数码产品': ['品牌', '型号', '内存容量', '电池效率', '保修情况'],
  '图书影音': ['作者', '出版社', '版本/印次', 'ISBN编号', '成色'],
  '农用物品': ['机械种类', '动力功率', '使用时长', '主要用途'],
  '文玩': ['材质', '年代/生产日期', '鉴定证书', '尺寸规格'],
  '母婴': ['品牌', '材质安全', '适用年龄', '消毒情况'],
  '潮玩': ['系列', '款式/稀有度', '盒子状态', '是否拆袋'],
  '户外': ['品牌', '重量/规格', '防水性能', '面料科技'],
  '家电': ['品牌', '能效等级', '外形尺寸', '功能完好度'],
  '家居日用': ['材质', '尺寸', '使用状态', '风格'],
  '美妆': ['品牌', '保质期/到期日', '是否拆封', '购买渠道'],
  '穿搭': ['品牌', '尺码', '面料成分', '适用季节'],
  '工艺礼品': ['工艺材质', '包装情况', '寓意主题', '产地']
}

const form = reactive({
  title: '',
  category: '',
  price: 0,
  desc: '',
  images: [],
  attributes: {} // 这里存储最终发给后端的 JSON 对象
})

const customAttrs = ref([]) // 用于存放用户手动增加的“键值对”
const dynamicFields = ref([]) // 当前分类对应的预设字段名列表
const selectedCatName = ref('')

const isEdit = computed(() => !!route.params.id)
const uploadHeaders = { Authorization: `Bearer ${localStorage.getItem('token')}` }

// 处理分类选择切换
const handleCategoryChange = (val) => {
  const cat = categories.value.find(item => item.id === val)
  if (!cat) return

  selectedCatName.value = cat.name
  
  // 🚀 2. 匹配模板：优先用后端传的，后端没有就匹配前端预设的
  let fields = cat.attribute_fields || []
  if (fields.length === 0) {
    // 模糊匹配分类名
    const templateKey = Object.keys(categoryTemplates).find(key => cat.name.includes(key))
    fields = categoryTemplates[templateKey] || []
  }
  
  dynamicFields.value = fields

  // 初始化属性对象
  if (!isEdit.value) {
    form.attributes = {}
    fields.forEach(f => { form.attributes[f] = '' })
  }
}

// 增加/删除自定义参数
const addCustomAttr = () => { customAttrs.value.push({ k: '', v: '' }) }
const removeCustomAttr = (index) => { customAttrs.value.splice(index, 1) }

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
        attributes: detail.attributes || {}
      })
      handleCategoryChange(detail.category)
    } finally {
      loading.value = false
    }
  }
})

const handleUploadSuccess = (res) => { form.images.push(res.url) }

const onSubmit = async () => {
  submitting.value = true
  
  // 🚀 3. 提交前合并自定义属性到 attributes 对象中
  customAttrs.value.forEach(item => {
    if (item.k && item.v) {
      form.attributes[item.k] = item.v
    }
  })

  try {
    if (isEdit.value) {
      await updateProduct(route.params.id, form)
      ElMessage.success('修改成功！')
    } else {
      await postProduct(form)
      ElMessage.success('发布成功！')
    }
    router.push('/my-products')
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.post-container { max-width: 900px; margin: 20px auto; }
.dynamic-attr-wrapper { background: #fcfcfc; padding: 10px; border-radius: 8px; margin-bottom: 20px; }
.custom-attr-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding-left: 40px;
  .split { color: #999; }
}
.img-preview-list { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;
  .preview-img { width: 100px; height: 100px; border-radius: 4px; border: 1px solid #eee; }
}
</style>