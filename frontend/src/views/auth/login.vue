<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>二手物品交易平台 - 登录</span>
        </div>
      </template>
      
      <!-- 绑定form数据 -->
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="账号" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入账号" />
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

        <!-- 验证码 -->
        <el-form-item label="验证码" prop="captcha">
          <div class="captcha-box">
            <el-input 
              v-model="loginForm.captcha" 
              placeholder="验证码" 
              maxlength="4"
              @keyup.enter="handleLogin"
            />
            <div class="captcha-img" title="点击刷新" @click="refreshCaptcha">
              {{ captchaText }}
            </div>
          </div>
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
import { ref, reactive, onMounted } from 'vue' 
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { getProfile } from '@/api/user'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)


const captchaText = ref('')


const refreshCaptcha = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789' 
  let code = ''
  for (let i = 0; i < 4; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaText.value = code
}

onMounted(() => {
  refreshCaptcha() 
})


const loginForm = reactive({
  username: '',
  password: '',
  captcha: '' 
})

// 表单验证规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

// 登录处理函数
const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (!valid) return; 


    if (loginForm.captcha.toUpperCase() !== captchaText.value.toUpperCase()) {
      ElMessage.error('验证码错误')
      refreshCaptcha()
      return
    }

    loading.value = true;
    try {
      const res = await login(loginForm);
      
      if (res && res.access) {
        localStorage.setItem('token', res.access);
        localStorage.setItem('username', res.username || loginForm.username); 
        localStorage.setItem('is_staff', res.is_staff ? 'true' : 'false');
        localStorage.setItem('is_superuser', res.is_superuser ? 'true' : 'false');
        
        ElMessage.success('登录成功，欢迎回来');
        window.location.href = '/';
      } else {
        console.error('服务器返回数据格式异常:', res);
      }

    } catch (error) {
      console.log('登录受阻:', error.response?.data);
      refreshCaptcha()
    } finally {
      loading.value = false;
    }
  });
};

</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100vh;
  padding-top: 15vh;
  background-color: #ffffff !important;
  background-image: none !important;
  
  .login-card {
    width: 400px;
    border-radius: 8px;
  }
  

  .captcha-box {
    display: flex;
    gap: 12px;
    width: 100%;
    .captcha-img {
      width: 120px;
      height: 40px;
      background: #eef1f6;
      color: #409eff;
      font-weight: bold;
      font-style: italic;
      font-size: 20px;
      letter-spacing: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      user-select: none;
      border-radius: 4px;
      border: 1px solid #dcdfe6;
      font-family: "Courier New", Courier, monospace;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
      &:hover {
        background: #e4e8f0;
      }
    }
  }

  .links {
    text-align: right;
    margin-top: 15px;
  }
}
</style>