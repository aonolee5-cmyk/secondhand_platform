from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    """聊天记录模型"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(verbose_name="消息内容")
    room_name = models.CharField(max_length=50, verbose_name="房间号") # 格式: user1_user2 (id小在前)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']