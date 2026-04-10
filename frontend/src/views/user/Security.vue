<template>
  <div class="security-container">
    <h2 class="page-title">账号与安全</h2>
    
    <!-- 🚀 安全等级提示 -->
    <el-alert
      :title="securityInfo.title"
      :type="securityInfo.type"
      :description="securityInfo.desc"
      show-icon
      :closable="false"
      class="security-banner"
    />

    <div class="security-list">
      <!-- 1. 登录密码 -->
      <div class="security-item">
        <div class="info">
          <div class="label">登录密码</div>
          <div class="status">建议定期更改密码，确保账号安全</div>
        </div>
        <div class="action">
          <el-button link type="primary" @click="pwdDialogVisible = true">修改</el-button>
        </div>
      </div>

      <el-divider />

      <!-- 2. 手机绑定 (从Profile同步状态) -->
      <div class="security-item">
        <div class="info">
          <div class="label">手机绑定</div>
          <div class="status">已绑定：{{ maskedMobile }}</div>
        </div>
        <div class="action">
          <el-button link type="primary" @click="mobileDialogVisible = true">修改手机号</el-button>
        </div>
        <!-- ... 在页面底部添加修改手机号的弹窗 ... -->
        <el-dialog v-model="mobileDialogVisible" title="修改绑定手机" width="400px">
          <el-form :model="mobileForm" :rules="mobileRules" ref="mobileFormRef" label-position="top">
            <el-alert 
              title="为了您的账号安全，请确保新手机号为您本人使用" 
              type="info" 
              show-icon 
              :closable="false"
              style="margin-bottom: 20px"
            />
            <el-form-item label="原手机号">
              <el-input :placeholder="maskedMobile" disabled />
            </el-form-item>
            <el-form-item label="新手机号" prop="new_mobile">
              <el-input v-model="mobileForm.new_mobile" placeholder="请输入11位新手机号" maxlength="11" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="mobileDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitMobileChange" :loading="mobileLoading">确认修改</el-button>
          </template>
        </el-dialog>
      </div>

      <el-divider />

      <!-- 3. 实名认证状态 -->
      <div class="security-item">
        <div class="info">
          <div class="label">实名状态</div>
          <div class="status" :class="user.is_verified ? 'text-success' : 'text-warning'">
            {{ user.is_verified ? '已完成实名认证' : '尚未实名认证' }}
          </div>
        </div>
        <div class="action">
          <el-button link type="primary" @click="$router.push('/user/profile?tab=verify')">查看</el-button>
        </div>
      </div>

      <el-divider />

      <!-- 4. 危险操作 -->
      <div class="security-item danger-zone">
        <div class="info">
          <div class="label">注销账号</div>
          <div class="status">账号一旦注销，所有交易数据将无法找回</div>
        </div>
        <div class="action">
          <el-button link type="danger" @click="handleDeleteAccount">注销</el-button>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdDialogVisible" title="修改登录密码" width="400px">
      <el-form :model="pwdForm" label-position="top">
        <el-form-item label="当前密码">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordChange">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getProfile } from '@/api/user'
import { ElMessage, ElMessageBox, timePickerDefaultProps } from 'element-plus'
import request from '@/utils/request'

const user = ref({})
const pwdDialogVisible = ref(false)
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })
const mobileDialogVisible = ref(false)
const mobileLoading = ref(false)
const mobileFormRef = ref(null)
const mobileForm = reactive({ new_mobile: '' })

// 安全等级计算
const securityInfo = computed(() => {
  if (user.value.is_verified && user.value.mobile) {
    return { title: '安全等级：高', type: 'success', desc: '您的账号非常安全，请继续保持。' }
  }
  return { title: '安全等级：中', type: 'warning', desc: '建议您尽快完成实名认证，以提升账号安全等级。' }
})

const maskedMobile = computed(() => {
  if (!user.value.mobile) return '未绑定'
  return user.value.mobile.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
})

const submitPasswordChange = async () => {
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    return ElMessage.error('两次输入的新密码不一致')
  }
  try {
    await request({ url: '/users/change-password/', method: 'post', data: pwdForm })
    ElMessage.success('密码已成功修改，请重新登录')
    // 修改成功后强制退出并重新登录
    localStorage.clear()
    window.location.href = '/'
  } catch (err) { /* 错误已由拦截器处理 */ }
}

const handleDeleteAccount = () => {
  ElMessageBox.confirm('注销账号是不可逆的操作，确定要离开吗？', '警告', {
    confirmButtonText: '确定注销',
    cancelButtonText: '我再想想',
    type: 'error'
  }).then(() => {
    ElMessage.error('该功能目前仅限联系客服人工注销')
  })
}

const mobileRules = {
  new_mobile: [
    { required: true, message: '请输入新手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号码', trigger: 'blur' }
  ]
}
// 校验手机号
const submitMobileChange = () => {
  mobileFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    mobileLoading.value = true
    try {
      const res = await request({ 
        url: '/users/change-mobile/', 
        method: 'post', 
        data: mobileForm 
      })
      
      ElMessage.success('手机号修改成功')
      // 更新本地显示的手机号
      user.value.mobile = mobileForm.new_mobile 
      mobileDialogVisible.value = false
      mobileForm.new_mobile = ''
    } catch (err) {
      // 错误已由拦截器处理 (例如：手机号已存在)
    } finally {
      mobileLoading.value = false
    }
  })
}

onMounted(async () => {
  user.value = await getProfile()
})
</script>

<style scoped lang="scss">
.security-container { padding: 30px; }
.security-banner { margin-bottom: 30px; border-radius: 8px; }
.security-list {
  .security-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    
    .label { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 5px; }
    .status { font-size: 14px; color: #999; }
    .text-success { color: #67C23A; font-weight: bold; }
    .text-warning { color: #E6A23C; }
  }
}
.danger-zone { .label { color: #F56C6C !important; } }
</style>