from .models import Address, Report, CreditLog, User
from rest_framework import serializers
from django.contrib.auth import get_user_model
from goods.models import Product, Category
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

User = get_user_model()

class CreditLogSerializer(serializers.ModelSerializer):
    ''' 
    信用积分记录
    '''
    class Meta:
        model = CreditLog
        fields = ['id', 'amount', 'reason', 'action_type', 'create_time']
        read_only_fields = ['user', 'created_time']

class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户信息
    """
    buy_count = serializers.SerializerMethodField()
    sell_count = serializers.SerializerMethodField()
    fav_count = serializers.SerializerMethodField()
    credit_logs = CreditLogSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'mobile', 'avatar', 'real_name', 'id_card', 'is_verified', 'credit_score', 'verify_status', 'buy_count', 'sell_count', 'fav_count', 'credit_logs', 'verify_time']
        read_only_fields = ['username', 'credit_score', 'is_verified']

    def get_buy_count(self, obj):
        return obj.buy_orders.count() 

    def get_sell_count(self, obj):
        return obj.sell_orders.count()

    def get_fav_count(self, obj):
        from trade.models import Favorite
        return Favorite.objects.filter(user=obj).count()
    
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']

class RegisterSerializer(serializers.ModelSerializer):
    """
    密码加密
    """
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'mobile', 'nickname']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次密码输入不一致")
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("该账号已存在")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class ReportSerializer(serializers.ModelSerializer):
    ''' 举报 '''
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['reporter', 'status']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'mobile', 'avatar']
        read_only_fields = ['username', 'credit_score', 'is_verified']
        

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'mobile', 'avatar', 
            'credit_score', 'is_verified', 'verify_status',
            'is_staff' 
        ]

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['is_staff'] = self.user.is_staff
        data['id'] = self.user.id
        return data
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        user = User.objects.filter(username=username).first()
        data = super().validate(attrs)
        if user and not user.is_active:
            raise serializers.ValidationError({
                "detail": "账号已被封禁"
            })

        

        # 验证通过并获取token
        data['username'] = self.user.username
        data['id'] = self.user.id
        data['is_staff'] = self.user.is_staff          
        data['is_superuser'] = self.user.is_superuser  
        
        return data
    
