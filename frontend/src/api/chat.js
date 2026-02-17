import request from '@/utils/request'

export function getChatHistory(targetId) {
  return request({ 
    url: '/chat/history/', 
    method: 'get', 
    params: { target_id: targetId } 
  })
}