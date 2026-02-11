<template>
  <div class="profile-container">
    <el-row :gutter="25">
      <!-- 左侧：用户卡片 (展示核心状态) -->
      <el-col :span="8">
        <el-card class="user-info-card" shadow="hover">
          <div class="user-avatar-box">
            <!-- 【修改点：包装了 el-upload 并在外层增加了 hover 效果】 -->
            <el-upload
              class="avatar-uploader"
              action=""
              :show-file-list="false"
              :http-request="handleAvatarUpload"
              :before-upload="beforeAvatarUpload"
            >
              <div class="avatar-wrapper">
                <el-avatar 
                  :size="100" 
                  :src="user.avatar ? 'http://127.0.0.1:8000' + user.avatar : 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" 
                />
                <div class="avatar-mask">
                  <el-icon><Camera /></el-icon>
                  <span>修改头像</span>
                </div>
              </div>
            </el-upload>

            <div class="user-status-tags">
              <el-tag :type="user.is_verified ? 'success' : 'info'" round size="small">
                <el-icon><CircleCheck v-if="user.is_verified" /><Warning v-else /></el-icon>
                {{ user.is_verified ? '身份已核验' : '未实名' }}
              </el-tag>
            </div>
          </div>

          <div class="user-basic-info">
            <h2 class="nickname">{{ user.nickname || user.username }}</h2>
            <p class="bio">{{ user.bio || '暂无个性签名' }}</p>
          </div>

          <el-divider />

          <!-- 信用展示 (结构图重点) -->
          <div class="credit-section">
            <div class="credit-header">
              <span>平台信用评分</span>
              <el-tooltip content="基于成交率、违约记录及评价加权计算" placement="top">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
            <div class="credit-value" :class="getCreditColor(user.credit_score)">
              {{ user.credit_score }}
            </div>
            <div class="credit-level">信用等级：{{ getCreditLevel(user.credit_score) }}</div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：功能管理区 -->
      <el-col :span="16">
        <el-tabs type="border-card" class="profile-tabs">
          
          <!-- 1. 个人信息管理 -->
          <el-tab-pane>
            <template #label>
              <span class="tab-label"><el-icon><User /></el-icon> 个人信息管理</span>
            </template>
            <el-form :model="user" label-width="100px" class="form-body">
              <el-form-item label="登录账号">
                <el-input v-model="user.username" disabled />
                <span class="input-tip">账号为唯一标识，不可修改</span>
              </el-form-item>
              <el-form-item label="个性昵称">
                <el-input v-model="user.nickname" placeholder="设置一个好听的昵称" />
              </el-form-item>
              <el-form-item label="联系手机">
                <el-input v-model="user.mobile" placeholder="用于接收订单通知" />
              </el-form-item>
              <el-form-item label="个性签名">
                <el-input v-model="user.bio" type="textarea" :rows="2" placeholder="向买家介绍一下自己" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleUpdate">保存资料修改</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 2. 实名认证 -->
          <el-tab-pane>
            <template #label>
              <span class="tab-label"><el-icon><Postcard /></el-icon> 实名认证</span>
            </template>
            
          <!-- 认证通过 ---->
          <div v-if="user.verify_status === 2" class="verified-box">
            <el-result icon="success" title="身份核验已通过" :sub-title="'真实姓名：' + maskName(user.real_name)">
              <template #extra>
                <p class="security-info">您的身份信息已加密处理，平台严格保障隐私安全</p>
                <el-tag type="success" effect="plain">已认证</el-tag>
              </template>
            </el-result>
          </div>

          <!--审核中-->
          <div v-else-if="user.verify_status === 1" class="pending-box">
            <el-result icon="warning" title="实名信息审核中" sub-title="管理员将在 24 小时内完成审核，请耐心等待">
              <template #extra>
                <el-button type="info" disabled>已提交审核</el-button>
              </template>
            </el-result>
          </div>

          <!-- 未认证 -->
          <div v-else class="unverified-box">
            <el-alert 
              v-if="user.verify_status === 3" 
              title="认证被驳回：请检查信息是否真实有效并重新提交" 
              type="error" 
              show-icon 
              style="margin-bottom: 20px" 
            />
            <el-alert title="实名认证须知" type="warning" show-icon :closable="false" style="margin-bottom: 25px">
                实名认证通过后可提升账号权重及买家信任度，是发布商品的前提。
            </el-alert>
            <el-form :model="verifyForm" label-width="100px" ref="verifyFormRef">
              <el-form-item label="真实姓名">
                <el-input v-model="verifyForm.real_name" placeholder="请输入身份证姓名" />
              </el-form-item>
              <el-form-item label="身份证号">
                <el-input v-model="verifyForm.id_card" placeholder="请输入18位二代身份证号" maxlength="18" />
              </el-form-item>
              <el-form-item>
                <el-button type="success" @click="handleVerify" :loading="verifying">提交实名申请</el-button>
              </el-form-item>
            </el-form>
          </div>
          </el-tab-pane>


          <el-tab-pane label="地址管理">
            <div style="margin-bottom: 20px;">
              <el-button type="primary" :icon="Plus" @click="openAddressDialog">新增收货地址</el-button>
            </div>

            <el-table :data="addressesList" style="width: 100%"> 
              <el-table-column prop="receiver" label="收货人" width="120" />
              <el-table-column prop="mobile" label="手机号" width="130" />
              <el-table-column label="收货地址">
                <template slot-scope="scope">
                  {{ scope.row.region }} {{scope.row.detail}}
                  <el-tag v-if="SCOPE.row.is_default" size="small" type="danger" style="margin-left: 10px;">默认</el-tag>
                </template>
              </el-table-column>
            <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button like type="primary" v-if="!scope.row.is_default" @click="handleSetDefault(scope.row.id)">设为默认</el-button>
                  <el-button like type="danger" @click="handleDeleteAddress(scope.row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-dialog v-model="addressDialogVisible" title="新增收货地址" width="500px">
              <el-form :model="addressForm" label-width="80px">
                <el-form-item label="收货人">
                  <el-input v-model="addressForm.receiver" placeholder="请输入收货人姓名" />
                </el-form-item>
                <el-form-item label="手机号">
                  <el-input v-model="addressForm.mobile" placeholder="请输入收货人手机号" />
                </el-form-item>
                <el-form-item label="所在地区">
                  <el-cascader 
                    v-model="addressForm.region" 
                    :options="regionOptions" 
                    placeholder="请选择所在地区"
                    style="width: 100%;"
                  />
                </el-form-item>
                <el-form-item label="详细地址">
                  <el-input v-model="addressForm.detail" placeholder="请输入详细地址信息" />
                </el-form-item>
                <el-form-item label="默认地址">
                  <el-switch v-model="addressForm.isDefault" />
                </el-form-item>
              </el-form>
              <template #footer>
                  <el-button @click="addressDialogVisible = false">取消</el-button>
                  <el-button type="primary" @click="submitAddress">确定</el-button>
              </template>
            </el-dialog>
          </el-tab-pane>

        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { 
  getProfile, updateProfile, updateAvatar,submitVerify, 
  getAddresses, addAddress, deleteAddress, setDefaultAddress } from '@/api/user'
import { ElMessage } from 'element-plus'
import { 
  User, Postcard, Location, QuestionFilled, 
  CircleCheck, Warning, Camera
} from '@element-plus/icons-vue'
import { el } from 'element-plus/es/locale/index.mjs'
import {Plus} from '@element-plus/icons-vue'


const user = ref({
  username: '',
  nickname: '',
  mobile: '',
  bio: '',
  avatar: '',
  credit_score: 0,
  is_verified: false,
  verify_status: 0, // 0-未认证，1-审核中，2-已认证，3-审核驳回
  real_name: '', // 实名认证后返回的真实姓名
})

const addressesList = ref([]) // 用户地址列表
const addressDialogVisible = ref(false)
const addressForm = reactive({
  receiver: '',
  mobile: '',
  region: [],
  detail: '',
  is_Default: false,
})

const avatarFile = ref(false)

const verifyForm = reactive({
  real_name: '',
  id_card: '',
})
// 获取用户资料
const fetchUserData = async () => {
  try {
    const res = await getProfile()
    user.value = res
  } catch (error) {
    console.error('获取用户资料失败:', error)
  }
}

onMounted(fetchUserData)

// 信用颜色计算
const getCreditColor = (score) => {
  if (score >= 90) return 'text-success'
  if (score >= 70) return 'text-primary'
  return 'text-danger'
}

// 信用等级计算
const getCreditLevel = (score) => {
  if (score >= 90) return '极好'
  if (score >= 70) return '良好'
  return '一般'
}

const verifying = ref(false)
// 名字脱敏显示
const maskName = (name) => {
  if (!name) return ''
  return name.charAt(0) + '*'.repeat(name.length - 1)
}

// 更新用户信息
const handleUpdate = async () => {
  await updateProfile({ 
    nickname: user.value.nickname,
    mobile: user.value.mobile,
    bio: user.value.bio 
  })
  ElMessage.success('个人资料保存成功')
  fetchUserData() 
}

const handleVerify = async () => {
  if (!verifyForm.real_name || !verifyForm.id_card) {
    ElMessage.error('请填写正确的身份信息')
    return
  }
  verifying.value = true
  try {
    await submitVerify(verifyForm)
    ElMessage.success('认证信息提交成功')
    fetchUserData() // 刷新状态变为“审核中”
  } catch (error) {
    console.error(error)
  } finally {
    verifying.value = false
  }
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('头像必须是 JPG/PNG 格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleAvatarUpload = async (options) => { 
  const formData = new FormData()
  // 注意：'avatar' 必须匹配后端 User 模型中的字段名
  formData.append('avatar', options.file)
  try {
    await updateAvatar(formData)
    ElMessage.success('头像更新成功')
    fetchUserData() // 刷新界面
  } catch (error) {
    console.error(error)
  }
}

const loadAddresses = async () => {
   const res = await getAddresses()
   addressesList.value = res.results || res
}

const loadProfile = async () => { 
  try {
    const res = await getProfile()
    console.log('后端返回数据：', res)
    profile.value = res
  } catch (error) {
    console.error(error)

  }
}

onMounted(() => {
  loadProfile()
  loadAddresses()
})
const openAddressDialog = () => {
  Object.assign(addressForm, { receiver: '',
   mobile: '', 
   region: '', 
   detail: '', 
   is_default: false })
  addressDialogVisible.value = true
}

const submitAddress = async () => {
  await addAddress(addressForm)
  ElMessage.success('地址添加成功')
  addressDialogVisible.value = false
  loadAddresses()
}

const handleDeleteAddress = async (id) => {
  await deleteAddress(id)
  ElMessage.success('已删除')
  loadAddresses()
}

const handleSetDefault = async (id) => {
  await setDefaultAddress(id)
  loadAddresses()
}

</script>

<style scoped lang="scss">
.profile-container { padding: 40px; max-width: 1100px; margin: 0 auto; }

/* 头像上传样式增强 */
.user-avatar-box {
  .avatar-uploader {
    cursor: pointer;
    .avatar-wrapper {
      position: relative;
      border-radius: 50%;
      overflow: hidden;
      width: 100px;
      height: 100px;
      &:hover .avatar-mask {
        opacity: 1;
      }
    }
    .avatar-mask {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.4);
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      opacity: 0;
      transition: opacity 0.3s;
      gap: 4px;
    }
  }
}

.user-info-card {
  border-radius: 12px;
  .user-avatar-box {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    .user-status-tags { margin-top: 12px; }
  }
  .user-basic-info {
    text-align: center;
    margin-top: 15px;
    .nickname { margin: 0; font-size: 20px; color: #303133; }
    .bio { color: #909399; font-size: 13px; margin-top: 8px; }
  }
}

.credit-section {
  text-align: center;
  padding: 10px 0;
  .credit-header {
    font-size: 12px; color: #999;
    display: flex; align-items: center; justify-content: center; gap: 4px;
  }
  .credit-value { font-size: 36px; font-weight: bold; margin: 8px 0; }
  .credit-level { font-size: 12px; color: #666; }
}

.profile-tabs { border-radius: 12px; min-height: 480px; }
.tab-label { display: flex; align-items: center; gap: 8px; }
.form-body { padding: 20px 10px; }
.input-tip { font-size: 12px; color: #999; margin-left: 10px; }
.verified-box { padding: 40px 0; }
.security-info { font-size: 12px; color: #999; }
.unverified-box { padding: 20px; }

/* 颜色辅助类 */
.text-success { color: #67C23A; }
.text-primary { color: #409EFF; }
.text-danger { color: #F56C6C; }
</style>