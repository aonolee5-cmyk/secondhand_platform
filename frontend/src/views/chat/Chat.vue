<template>
  <div class="chat-container">
    <el-card class="chat-box">
      <template #header>
        <div class="header">
          <span>与 {{ targetName }} 的对话</span>
          <el-tag v-if="status === 'connected'" type="success" size="small">在线</el-tag>
          <el-tag v-else type="danger" size="small">离线</el-tag>
        </div>
      </template>

      <!-- 消息列表区域 -->
      <div class="msg-list" ref="msgListRef">
        <div 
          v-for="msg in messages" 
          :key="msg.id" 
          class="msg-item"
          :class="{ 'is-me': msg.sender === myId }"
        >
          <!-- 对方头像 -->
          <el-avatar v-if="msg.sender !== myId" :size="36" class="avatar left" icon="UserFilled" />
          
          <div class="bubble">
            {{ msg.content }}
          </div>
          
          <!-- 我的头像 -->
          <el-avatar v-if="msg.sender === myId" :size="36" class="avatar right" icon="UserFilled" />
        </div>
      </div>

      <!-- 输入框区域 -->
      <div class="input-area">
        <el-input 
          v-model="inputMsg" 
          placeholder="请输入消息..." 
          @keyup.enter="sendMessage"
        >
          <template #append>
            <el-button @click="sendMessage" type="primary">发送</el-button>
          </template>
        </el-input>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getProfile } from '@/api/user'
import { getChatHistory } from '@/api/chat'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const targetId = parseInt(route.params.targetId) // 对方ID
const targetName = route.query.name || '卖家'
const myId = ref(null)

const messages = ref([])
const inputMsg = ref('')
const status = ref('disconnected')
const msgListRef = ref(null)
let socket = null

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (msgListRef.value) {
    msgListRef.value.scrollTop = msgListRef.value.scrollHeight
  }
}

// 初始化
onMounted(async () => {
  // 1. 获取我的ID
  const profile = await getProfile()
  myId.value = parseInt(profile.id)

  await request({
    url:'/chat/history/mark_read/',
    method:'post',
    data:{target_id:targetId}
  })

  // 2. 加载历史记录
  const history = await getChatHistory(targetId)
  messages.value = history.results || history
  scrollToBottom()

  // 3. 建立 WebSocket 连接
  // 房间号逻辑：小ID_大ID (与后端一致)
  const rawIds = [myId.value, parseInt(targetId)]
  const sortedIds = rawIds.sort((a, b) => a - b) 
  const roomName = `${sortedIds[0]}_${sortedIds[1]}`
  
  console.log('DEBUG: 我的ID:', myId.value, '对方ID:', targetId, '计算出的房间名:', roomName)
  
  // 注意：WebSocket 地址前缀是 ws://
  socket = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${roomName}/`)

  socket.onopen = () => {
    status.value = 'connected'
    console.log('WebSocket已连接')
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    // 将新消息推入列表
    messages.value.push({
      id: Date.now(), // 临时ID
      sender: data.sender_id,
      content: data.message,
      timestamp: new Date()
    })
    scrollToBottom()
  }

  socket.onclose = () => {
    status.value = 'disconnected'
  }
})

// 发送消息
const sendMessage = () => {
  if (!inputMsg.value.trim()) return
  if (status.value !== 'connected') {
    ElMessage.error('网络连接已断开')
    return
  }

  // 发送 JSON 字符串
  socket.send(JSON.stringify({
    message: inputMsg.value,
    sender_id: myId.value,
    receiver_id: targetId
  }))

  inputMsg.value = ''
}

// 销毁时断开
onUnmounted(() => {
  if (socket) socket.close()
})
</script>

<style scoped lang="scss">
.chat-container { max-width: 800px; margin: 20px auto; }
.chat-box { height: 600px; display: flex; flex-direction: column; }
.header { display: flex; justify-content: space-between; align-items: center; }

.msg-list {
  height: 450px;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #eee;
}

.msg-item {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
  
  &.is-me {
    justify-content: flex-end;
    .bubble {
      background-color: #95ec69; // 微信绿
      color: #000;
      margin-right: 10px;
      margin-left: 0;
      &::after {
        left: auto; right: -8px;
        border-color: transparent transparent transparent #95ec69;
      }
    }
  }
}

.avatar { flex-shrink: 0; }
.left { margin-right: 10px; }
.right { margin-left: 10px; }

.bubble {
  max-width: 70%;
  padding: 10px 15px;
  background-color: #fff;
  border-radius: 4px;
  position: relative;
  word-break: break-all;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  
  // 小三角
  &::after {
    content: '';
    position: absolute;
    top: 10px;
    left: -8px;
    width: 0; height: 0;
    border-style: solid;
    border-width: 6px 8px 6px 0;
    border-color: transparent #fff transparent transparent;
  }
}

.input-area { padding: 20px; }
</style>