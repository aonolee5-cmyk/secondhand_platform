from .models import Address
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    用于展示用户信息
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'mobile', 'avatar', 'real_name', 'id_card', 'is_verified', 'credit_score']
        read_only_fields = ['username', 'credit_score', 'is_verified']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']

class RegisterSerializer(serializers.ModelSerializer):
    """
    用于注册：处理密码加密
    """
    # 确认密码字段
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'mobile']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次密码输入不一致")
        return attrs

    def create(self, validated_data):
        # 删除 password_confirm，因为它不是模型字段
        validated_data.pop('password_confirm')
        # 使用 create_user 方法，它会自动对密码进行加密哈希
        user = User.objects.create_user(**validated_data)
        return user