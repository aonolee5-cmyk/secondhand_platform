<template>
  <div class="chat-list-container">
    <el-card header="最近消息">
      <el-empty v-if="contacts.length === 0" description="暂无消息" />
      <div 
        v-for="item in contacts" 
        :key="item.id" 
        class="contact-item"
        @click="goToChat(item)"
      >
        <el-badge is-dot :hidden="item.is_read || item.sender === myId">
          <el-avatar icon="UserFilled" />
        </el-badge>
        <div class="info">
          <div class="top">
            <!-- 逻辑：如果我是发送者，显示接收者名字；如果我是接收者，显示发送者名字 -->
            <span class="name">系统用户 {{ item.sender === myId ? '对方' : '联系人' }}</span>
            <span class="time">{{ formatTime(item.timestamp) }}</span>
          </div>
          <div class="last-msg">{{ item.content }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { getProfile } from '@/api/user' // 必须引入这个

const router = useRouter()
const contacts = ref([])
const myId = ref(null)
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const profile = await getProfile()
    myId.value = profile.id
    
    const res = await request({ url: '/chat/history/list_recent_contacts/', method: 'get' })
    contacts.value = res.results || []
    
    console.log('DEBUG: 列表数据', contacts.value)
  } catch (err) {
    console.error('加载失败', err)
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${date.getMinutes()}`
}

// 获取对方的名字（辅助函数）
const getTargetName = (item) => {
  return item.sender === myId.value ? `用户(ID:${item.receiver})` : `用户(ID:${item.sender})`
}

const goToChat = (item) => {
  const targetId = item.sender === myId.value ? item.receiver : item.sender
  router.push(`/chat/${targetId}`)
}

onMounted(loadData)
</script>

<style scoped>
.contact-item { display: flex; align-items: center; padding: 15px; cursor: pointer; border-bottom: 1px solid #f0f0f0; }
.contact-item:hover { background: #f9f9f9; }
.info { flex: 1; margin-left: 15px; }
.top { display: flex; justify-content: space-between; margin-bottom: 5px; }
.name { font-weight: bold; }
.time { font-size: 12px; color: #999; }
.last-msg { font-size: 13px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 300px; }
</style>