<template>
  <div class="profile-content">
    <div class="user-header-banner">
      <div class="user-info-box">
        <el-upload
          class="avatar-uploader"
          action=""
          :show-file-list="false"
          :http-request="handleAvatarUpload"
          :before-upload="beforeAvatarUpload"
        >
          <div class="big-avatar-wrapper">
            <el-avatar 
              :size="100" 
              :src="fullAvatarUrl || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" 
            />
            <div class="avatar-edit-mask"><el-icon><Camera /></el-icon></div>
          </div>
        </el-upload>

        <div class="text-info">
          <h2 class="username">{{ user.nickname || user.username }}</h2>
          <div class="status-tags">
            <el-tag v-if="user.is_verified" type="success" size="small" round effect="dark">
              <el-icon><CircleCheck /></el-icon> 身份已核验
            </el-tag>
            <el-tag v-else type="info" size="small" round effect="plain">未实名</el-tag>
            <span class="bio-text">{{ user.bio || '还没有个性签名哦~' }}</span>
          </div>
        </div>
        
        <div class="header-actions">
          <el-button round class="edit-btn" @click="activeTab = 'settings'">
             <el-icon><EditPen /></el-icon> 编辑资料
          </el-button>
        </div>
      </div>
    </div>

    <!--  底部功能区  -->
    <div class="tabs-container">
      <el-tabs v-model="activeTab" class="custom-tabs">
        
        <!-- 标签页：我的宝贝 -->
        <el-tab-pane label="宝贝" name="goods">
          <div v-loading="loadingProducts" class="goods-content">
            
            <el-row :gutter="20" v-if="myProducts.length > 0">
              <el-col :span="8" v-for="item in myProducts" :key="item.id" style="margin-bottom: 20px">
                <el-card :body-style="{ padding: '0px' }" class="mini-product-card" shadow="hover">
                  <!-- 商品图片 -->
                  <div class="image-container">
                    <el-image 
                      :src="'http://127.0.0.1:8000' + item.images[0]" 
                      fit="cover" 
                      class="prod-img"
                    />
                    <el-tag 
                      class="status-tag" 
                      :type="item.status === 'onsale' ? 'success' : 'info'" 
                      effect="dark"
                    >
                      {{ item.status === 'onsale' ? '在售' : (item.status === 'audit' ? '审核中' : '已下架') }}
                    </el-tag>
                  </div>

                  <div style="padding: 10px">
                    <div class="prod-title">{{ item.title }}</div>
                    <div class="prod-footer">
                      <span class="price">￥{{ item.price }}</span>
                      <el-button link type="primary" @click="$router.push('/edit/' + item.id)">管理</el-button>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>


            <el-empty v-else description="您还没有发布过任何宝贝哦" :image-size="120">
              <el-button type="primary" round @click="$router.push('/post')">去发布一个</el-button>
            </el-empty>
            
          </div>
        </el-tab-pane>

        <!-- 信用及评价  -->
        <el-tab-pane label="信用及评价" name="credit">
          <div class="credit-card-dashboard">
            <div class="credit-main">
              <div class="score-num" :class="getCreditColor(user.credit_score)">{{ user.credit_score }}</div>
              <div class="score-label">平台信用评分</div>
              <el-rate :model-value="creditStar" disabled />
            </div>
            <div class="credit-history-section" style="margin-top: 30px;">
              <div class="section-title">
                <el-icon><Histogram /></el-icon> 信用成长足迹
              </div>
              
              <el-table :data="creditLogs" size="small" class="history-table" v-loading="loadingLogs">
                <el-table-column prop="create_time" label="记录时间" width="180">
                  <template #default="scope">
                    {{ formatDate(scope.row.create_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="reason" label="变动事项" />
                <el-table-column label="分值变动" width="120" align="center">
                  <template #default="scope">
                    <span :class="scope.row.amount > 0 ? 'score-up' : 'score-down'">
                      {{ scope.row.amount > 0 ? '+' : '' }}{{ scope.row.amount }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
              
              <div class="credit-tips">
                <el-alert 
                  title="信用分说明：上限 100 分。成功发布商品、完成交易及优质评价均可获得信用奖励。" 
                  type="info" 
                  :closable="false" 
                  show-icon 
                />
              </div>
            </div>
          </div>
          </el-tab-pane>


        <el-tab-pane label="地址管理" name="address">
          <div class="address-header">
            <el-button type="primary" :icon="Plus" @click="openAddressDialog">新增收货地址</el-button>
          </div>
          <el-table :data="addressesList" style="width: 100%" class="modern-table"> 
            <el-table-column prop="receiver" label="收货人" width="120" />
            <el-table-column prop="mobile" label="手机号" width="130" />
            <el-table-column label="详细地址">
              <template #default="scope">
                {{ scope.row.region }} {{scope.row.detail}}
                <el-tag v-if="scope.row.is_default" size="small" type="danger" effect="plain" style="margin-left: 10px;">默认</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="right">
              <template #default="scope">
                <el-button link type="primary" v-if="!scope.row.is_default" @click="handleSetDefault(scope.row.id)">设为默认</el-button>
                <el-button link type="primary" @click="handleEditAddress(scope.row)">编辑</el-button>
                <el-button link type="danger" @click="handleDeleteAddress(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>


        <el-tab-pane label="个人资料" name="settings">
          <el-collapse v-model="activeCollapse">
            <el-collapse-item title="基本资料修改" name="1">
              <el-form :model="user" label-width="100px" style="max-width: 500px">
                <el-form-item label="用户名"><el-input v-model="user.nickname" /></el-form-item>
                <el-form-item label="个性签名"><el-input v-model="user.bio" type="textarea" /></el-form-item>
                <el-form-item><el-button type="primary" @click="handleUpdate">保存资料</el-button></el-form-item>
              </el-form>
            </el-collapse-item>

            <el-collapse-item title="实名身份认证" name="2">
              <div v-if="user.verify_status === 2">
                <el-result icon="success" title="已通过实名认证" :sub-title="'真实姓名：' + maskName(user.real_name)">
                  <template #extra><el-tag type="success">认证终身有效</el-tag></template>
                </el-result>
              </div>
              <div v-else-if="user.verify_status === 1">
                <el-result icon="warning" title="审核中" sub-title="预计 24 小时内完成" />
              </div>
              <div v-else>
                <el-form :model="verifyForm" :rules="verifyRules" ref="verifyFormRef" label-width="100px">
                  <el-form-item label="真实姓名" prop="real_name"><el-input v-model="verifyForm.real_name" /></el-form-item>
                  <el-form-item label="身份证号" prop="id_card"><el-input v-model="verifyForm.id_card" /></el-form-item>
                  <el-form-item><el-button type="success" @click="handleVerify" :loading="verifying">提交申请</el-button></el-form-item>
                </el-form>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-tab-pane>
      </el-tabs>
    </div>


    <el-dialog v-model="addressDialogVisible" :title="isEdit ?  '修改收货地址' :'新增收货地址' " width="500px">
      <el-form :model="addressForm" label-width="80px">
        <el-form-item label="收货人"><el-input v-model="addressForm.receiver" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="addressForm.mobile" /></el-form-item>
        <el-form-item label="所在地区">
          <el-cascader v-model="addressForm.regionCode" :options="regionData" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="详细地址"><el-input v-model="addressForm.detail" /></el-form-item>
        <el-form-item label="默认地址"><el-switch v-model="addressForm.is_default" /></el-form-item>
      </el-form>
      <template #footer>
          <el-button @click="addressDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAddress">确定保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import request from '@/utils/request' 
import { 
  getProfile, updateProfile, updateAvatar, submitVerify, 
  getAddresses, addAddress, deleteAddress, setDefaultAddress, updateAddress 
} from '@/api/user'
import { ElMessage } from 'element-plus'
import { 
  Camera, Plus, CircleCheck, EditPen, Goods, 
  User, Star, Setting, Histogram 
} from '@element-plus/icons-vue'
import { regionData, codeToText } from 'element-china-area-data' 
import { getMyProducts } from '@/api/goods' 



// --- 状态数据 ---
const user = ref({ credit_score: 70, avatar:'', nickname:'', mobile:'', bio:'', verify_status:0})
const activeTab = ref('goods')
const activeCollapse = ref(['1', '2'])
const addressesList = ref([])
const addressDialogVisible = ref(false)
const verifying = ref(false)
const verifyFormRef = ref(null)
const myProducts = ref([])
const creditLogs = ref([]) 
const loadingProducts = ref(false)
const loadingLogs = ref(false)

const isEdit = ref(false)
const editId = ref(null)

const verifyForm = reactive({ real_name: '', id_card: '' })
const addressForm = reactive({ receiver: '', mobile: '', regionCode:[], detail: '', is_default: false })


const creditStar = computed(() => user.value.credit_score / 20)

const fullAvatarUrl = computed(() => {
  if (!user.value.avatar) return ''
  if (user.value.avatar.startsWith('http')) return user.value.avatar
  return `http://127.0.0.1:8000${user.value.avatar}`
})




const initData = async () => {
  try {
    const profileRes = await getProfile()
    user.value = { ...profileRes }
    creditLogs.value = profileRes.credit_logs || [] 

    // 获取该用户的商品列表
    loadingProducts.value = true
    const prodRes = await getMyProducts()
    myProducts.value = prodRes.results || prodRes
    
    // 获取地址列表
    const addrRes = await getAddresses()
    addressesList.value = addrRes.results || addrRes
    
  } catch (err) {
    console.error('数据加载失败', err)
  } finally {
    loadingProducts.value = false
  }
}


const refreshProfile = async () => {
  const res = await getProfile()
  user.value = { ...res }
}

// 格式化时间函数
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const handleUpdate = async () => {
  await updateProfile({ 
    nickname: user.value.nickname, 
    mobile: user.value.mobile, 
    bio: user.value.bio 
  })
  ElMessage.success('资料保存成功')
  refreshProfile() 
}

const handleAvatarUpload = async (options) => { 
  const formData = new FormData()
  formData.append('avatar', options.file)
  try {
    await updateAvatar(formData)
    ElMessage.success('头像已更新')
    refreshProfile() 
  } catch (err) {
    ElMessage.error('头像上传失败')
  }
}

const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJPG) ElMessage.error('仅支持JPG/PNG')
  return isJPG
}

const verifyRules = {
  real_name: [{ required: true, message: '姓名必填', trigger: 'blur' }, { pattern: /^[\u4e00-\u9fa5]{2,10}$/, message: '请输入中文姓名' }],
  id_card: [{ required: true, message: '身份证必填', trigger: 'blur' }, { pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/, message: '格式错误' }]
}

const handleVerify = () => {
  verifyFormRef.value.validate(async (valid) => {
    if (!valid) return
    verifying.value = true
    try {
      await submitVerify(verifyForm)
      ElMessage.success('已提交申请')
      refreshProfile()
    } finally { verifying.value = false }
  })
}

const submitAddress = async () => {
  const regionText = addressForm.regionCode.map(code => codeToText[code]).join(' ')
  await addAddress({ ...addressForm, region: regionText })
  addressDialogVisible.value = false
  initData() // 刷新列表
}

const handleDeleteAddress = async (id) => { await deleteAddress(id); initData() }
const handleSetDefault = async (id) => { await setDefaultAddress(id); initData() }

const maskName = (n) => n ? n[0] + '*'.repeat(n.length - 1) : ''
const getCreditColor = (s) => s >= 90 ? 'text-success' : (s >= 70 ? 'text-primary' : 'text-danger')
const getCreditLevel = (s) => s >= 90 ? '极好' : (s >= 70 ? '良好' : '一般')
const openAddressDialog = () => { 
  isEdit.value = false
  editId.value = null
  Object.assign(addressForm, { receiver: '', mobile: '', regionCode:[], detail: '', is_default: false })
  addressDialogVisible.value = true 
}

const handleEditAddress = (row) => {
  isEdit.value = true
  editId.value = row.id
  
  addressForm.receiver = row.receiver
  addressForm.mobile = row.mobile
  addressForm.detail = row.detail
  addressForm.is_default = row.is_default
  
  
  addressForm.regionCode = [] 
  
  addressDialogVisible.value = true
}

const loadProfile = async () => {
  try {
    const res = await getProfile()
    user.value = res
    creditLogs.value = res.credit_logs || []
    
    console.log('信用日志数据:', creditLogs.value) 
  } catch (err) {
    console.error(err)
  }
}

onMounted(initData)
</script>

<style scoped lang="scss">
.profile-content {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.user-header-banner {
  height: 200px;
  background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
  position: relative;
  .user-info-box {
    position: absolute;
    bottom: -40px;
    left: 40px;
    right: 40px;
    display: flex;
    align-items: flex-end;
    
    .big-avatar-wrapper {
      position: relative;
      cursor: pointer;
      .big-avatar { border: 4px solid #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
      .avatar-edit-mask {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.3); border-radius: 50%; opacity: 0;
        display: flex; align-items: center; justify-content: center; color: #fff; font-size: 20px;
        transition: 0.3s;
      }
      &:hover .avatar-edit-mask { opacity: 1; }
    }

    .text-info {
      margin-left: 20px;
      margin-bottom: 45px;
      .username { font-size: 26px; font-weight: bold; margin: 0 0 10px; color: #333; }
      .status-tags { display: flex; align-items: center; gap: 10px; .bio-text { font-size: 13px; color: #666; } }
    }

    .header-actions { margin-left: auto; margin-bottom: 45px; .edit-btn { background: #333; color: #fff; border: none; } }
  }
}

.tabs-container {
  margin-top: 60px;
  padding: 0 40px 40px;
  :deep(.custom-tabs) {
    .el-tabs__item { font-size: 16px; font-weight: bold; height: 50px; }
    .el-tabs__active-bar { background-color: #ffda00; height: 4px; }
  }
}

.credit-card-dashboard {
  display: flex;
  align-items: center;
  background: #f8faff;
  padding: 30px;
  border-radius: 12px;
  .credit-main {
    text-align: center;
    padding-right: 40px;
    .score-num { font-size: 48px; font-weight: 800; line-height: 1; margin-bottom: 10px; }
    .score-label { font-size: 12px; color: #999; margin-bottom: 5px; }
  }
  .credit-details { padding-left: 40px; p { margin: 5px 0; color: #444; } .tip { font-size: 12px; color: #999; } }
}

.modern-table { margin-top: 15px; --el-table-header-bg-color: #f5f7fa; }
.text-success { color: #67C23A; } .text-primary { color: #409EFF; } .text-danger { color: #F56C6C; }
</style>