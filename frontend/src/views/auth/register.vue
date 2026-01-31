<template>
  <div class="auth-container">
    <el-card class="auth-card" header="用户注册">
      <el-form :model="regForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="regForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="regForm.mobile" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="regForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="regForm.password_confirm" type="password" show-password />
        </el-form-item>
        <el-button type="primary" @click="handleRegister" style="width: 100%">立即注册</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const regForm = reactive({
  username: '',
  mobile: '',
  password: '',
  password_confirm: ''
})

const handleRegister = async () => {
  try {
    await register(regForm)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (err) {
    // 错误已由拦截器处理
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; padding-top: 100px; }
.auth-card { width: 400px; }
</style>