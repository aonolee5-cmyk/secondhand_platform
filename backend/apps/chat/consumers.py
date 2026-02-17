import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 获取 URL 中的房间号 (例如: 1_2)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # 加入 Redis 频道组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 离开组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 接收前端发来的消息
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        receiver_id = text_data_json['receiver_id']
        
        print(f'DEBUG:收到消息-发送者{sender_id},接收者{receiver_id},房间{self.room_group_name}')

        # 保存到数据库
        await self.save_message(sender_id, receiver_id, message)

        # 广播给组内的所有人 (包括自己)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id
            }
        )

    # 处理组内广播的消息
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        # 保证房间名一致性: id小的在前
        ids = sorted([int(sender_id), int(receiver_id)])
        room_name = f"{ids[0]}_{ids[1]}"
        
        Message.objects.create(
            sender=sender, receiver=receiver, 
            content=message, room_name=room_name
        )