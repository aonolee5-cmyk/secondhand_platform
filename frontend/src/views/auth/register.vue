<template>
  <div class="auth-container">
    <el-card class="auth-card" shadow="always">
      <template #header>
        <div class="card-header">
          <span class="title">用户注册</span>
        </div>
      </template>

      <el-form :model="regForm" :rules="regRules" ref="regFormRef" label-width="90px" label-position="left">
        <!-- 账号  -->
        <el-form-item label="账号名" prop="username">
          <el-input v-model="regForm.username" placeholder="建议使用数字或英文" />
        </el-form-item>

        <!-- 用户名  -->
        <el-form-item label="用户名" prop="nickname">
          <el-input v-model="regForm.nickname" placeholder="请输入用户名" />
        </el-form-item>

        <!-- 手机号 -->
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model="regForm.mobile" placeholder="请输入11位手机号" maxlength="11" />
        </el-form-item>

        <!-- 密码 -->
        <el-form-item label="设置密码" prop="password">
          <el-input v-model="regForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>

        <!-- 确认密码 -->
        <el-form-item label="确认密码" prop="password_confirm">
          <el-input v-model="regForm.password_confirm" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>

        <div class="submit-section">
          <el-button type="primary" class="reg-btn" @click="handleRegister" :loading="loading">立即注册</el-button>
          <div class="footer-links">
            已有账号？<el-link type="primary" @click="$router.push('/login')">返回登录</el-link>
          </div>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const regFormRef = ref(null)
const loading = ref(false)

const regForm = reactive({
  username: '',
  nickname: '',
  mobile: '',
  password: '',
  password_confirm: ''
})

// 校验规则
const regRules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 4, max: 15, message: '账号长度在 4 到 15 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '账号只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入显示用户名', trigger: 'blur' },
    { min: 2, max: 10, message: '名称长度在 2 到 10 个字符', trigger: 'blur' }
  ],
  mobile: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== regForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

const handleRegister = () => {
  regFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await register(regForm)
      ElMessage.success('注册成功，请使用账号登录')
      router.push('/login')
    } catch (err) {
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}
.auth-card {
  width: 450px;
  border-radius: 12px;
  .title { font-size: 20px; font-weight: bold; color: #333; }
}
.submit-section {
  margin-top: 30px;
  .reg-btn { width: 100%; height: 45px; font-size: 16px; border-radius: 8px; }
  .footer-links { margin-top: 15px; text-align: center; font-size: 14px; color: #999; }
}
</style>