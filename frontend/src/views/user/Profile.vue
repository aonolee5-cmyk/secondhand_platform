<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧：个人基本信息 -->
      <el-col :span="8">
        <el-card class="box-card">
          <div class="user-header">
            <el-avatar :size="80" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
            <h2>{{ user.username }}</h2>
            <el-tag :type="user.is_verified ? 'success' : 'warning'">
              {{ user.is_verified ? '已实名认证' : '未实名' }}
            </el-tag>
          </div>
          <div class="user-stats">
            <div class="stat-item">
              <span class="label">信用分</span>
              <span class="value">{{ user.credit_score }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：详情与实名表单 -->
      <el-col :span="16">
        <el-tabs type="border-card">
          <el-tab-pane label="基本资料">
            <el-form :model="user" label-width="100px">
              <el-form-item label="手机号">
                <el-input v-model="user.mobile" />
              </el-form-item>
              <el-button type="primary" @click="handleUpdate">保存修改</el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="实名认证">
            <div v-if="user.is_verified">
              <el-result icon="success" title="您已通过实名认证" :sub-title="'真实姓名：' + user.real_name" />
            </div>
            <el-form v-else :model="verifyForm" label-width="100px">
              <el-alert title="实名认证后才能发布高价值商品，请如实填写" type="info" show-icon style="margin-bottom: 20px" />
              <el-form-item label="真实姓名">
                <el-input v-model="verifyForm.real_name" />
              </el-form-item>
              <el-form-item label="身份证号">
                <el-input v-model="verifyForm.id_card" />
              </el-form-item>
              <el-button type="success" @click="handleVerify">提交认证申请</el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="地址管理">
             <!-- 之后在这里实现地址列表 -->
             <p>地址管理功能正在按照计划开发中...</p>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { getProfile, updateProfile } from '@/api/user'
import { ElMessage } from 'element-plus'

const user = ref({})
const verifyForm = reactive({ real_name: '', id_card: '' })

onMounted(async () => {
  const res = await getProfile()
  user.value = res
})

const handleUpdate = async () => {
  await updateProfile({ mobile: user.value.mobile })
  ElMessage.success('更新成功')
}

const handleVerify = async () => {
  // 实名认证逻辑：提交给后端，后端由管理员审核
  await updateProfile({ 
    real_name: verifyForm.real_name, 
    id_card: verifyForm.id_card 
  })
  ElMessage.success('实名信息已提交，请等待系统同步')
  user.value.is_verified = true // 演示用，实际应由后台审核
}
</script>

<style scoped>
.user-header { text-align: center; padding: 20px 0; }
.user-stats { display: flex; justify-content: space-around; margin-top: 20px; border-top: 1px solid #eee; padding-top: 20px; }
.stat-item { text-align: center; }
.stat-item .label { display: block; color: #999; font-size: 12px; }
.stat-item .value { font-size: 20px; font-weight: bold; color: #409eff; }
</style>