from rest_framework import serializers
from .models import Message
from users.serializers import UserSerializer # 用户信息

class MessageSerializer(serializers.ModelSerializer):
    sender_info = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'