<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>二手交易平台 - 登录</span>
        </div>
      </template>
      
      <!-- 绑定 form 数据 -->
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            show-password
            @keyup.enter="handleLogin" 
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%;" @click="handleLogin">
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="links">
        <el-link type="primary">注册账号</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// 引入刚才定义的 API
import { login } from '@/api/auth'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

// 响应式表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 登录处理函数
const handleLogin = () => {
  if (!loginFormRef.value) return
  
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 1. 调用真实后端接口
        // 后端返回的数据结构通常是: { access: "...", refresh: "..." }
        const res = await login(loginForm)
        
        console.log('登录成功，后端返回:', res)
        
        // 2. 存储 Token (注意：simplejwt 返回的是 access)
        if (res.access) {
            localStorage.setItem('token', res.access)
            localStorage.setItem('refresh_token', res.refresh) // 可选：用于刷新
            
            ElMessage.success('登录成功')
            router.push('/') // 跳转首页
        } else {
            ElMessage.error('登录失败：未获取到令牌')
        }

      } catch (error) {
        console.error('登录报错:', error)
        // 错误提示已在 request.js 拦截器中统一处理，这里不用写了
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
  background-image: url('https://gw.alipayobjects.com/zos/rmsportal/TVYTbAXWheQpRcWDaDMu.svg'); /* 加个背景纹理 */
  
  .login-card {
    width: 400px;
    border-radius: 8px;
  }
  
  .links {
    text-align: right;
    margin-top: 15px;
  }
}
</style>