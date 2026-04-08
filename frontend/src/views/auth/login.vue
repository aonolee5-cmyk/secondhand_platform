<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>二手交易平台 - 登录</span>
        </div>
      </template>
      
      <!-- 绑定form数据 -->
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
        <el-link type="primary" :underline="false" @click="$router.push('/register')">注册账号</el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { getProfile } from '@/api/user'

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
  // 1. 表单预校验
  loginFormRef.value.validate(async (valid) => {
    if (!valid) return; // 如果前端校验没通过，直接返回

    loading.value = true;
    try {
      // 2. 调用登录接口
      const res = await login(loginForm);
      
      // 🚀【核心修改点】判断 res 是否存在，以及是否存在 access
      // 这样即便 request.js 没拦截住，这里也不会报错崩溃
      if (res && res.access) {
        // 3. 存储凭证与用户信息
        localStorage.setItem('token', res.access);
        // 存储 username，确保 App.vue 能识别身份
        localStorage.setItem('username', res.username || loginForm.username); 
        // 存储 staff 标记，注意：localStorage 存的是字符串
        localStorage.setItem('is_staff', res.is_staff ? 'true' : 'false');
        
        ElMessage.success('登录成功，欢迎回来');
        
        // 4. 执行跳转
        // 企业级建议：使用 window.location.href 强刷页面，彻底重置所有内存中的 Vue 状态
        window.location.href = '/';
      } else {
        // 如果后端返回了 200 OK 但没有 access（极少见），给予提示
        console.error('服务器返回数据格式异常:', res);
      }

    } catch (error) {
      // 🚀 逻辑跳转：当账号被封禁（后端返回 400/403）时，
      // axios 拦截器会 reject(error)，代码会自动跳到这里。
      // 此时 res 是 undefined，if(res.access) 根本不会运行，从而避免了崩溃。
      
      console.log('登录受阻，详细错误信息:', error.response?.data);
      // 具体的错误弹窗提示已经在 request.js 的拦截器里处理过了，这里保持安静即可
    } finally {
      loading.value = false;
    }
  });
};

const syncAuthState = () => {
  const token = localStorage.getItem('token')
  const name = localStorage.getItem('username')
  // 关键：localStorage 存的是字符串，判断时要处理
  const isStaff = localStorage.getItem('is_staff') === 'true'
  
  isLogin.value = !!token
  
  // 只要是 staff，不管叫什么名字，都能看到后台
  isAdmin.value = isLogin.value && isStaff
  
  // 备用兜底：如果就是想让 lee 必进
  if (name === 'lee') isAdmin.value = true
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