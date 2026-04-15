from .models import Address, Report
from rest_framework import serializers
from django.contrib.auth import get_user_model
from goods.models import Product, Category
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    用于展示用户信息
    """
    buy_count = serializers.SerializerMethodField()
    sell_count = serializers.SerializerMethodField()
    fav_count = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'mobile', 'avatar', 'real_name', 'id_card', 'is_verified', 'credit_score', 'verify_status', 'buy_count', 'sell_count', 'fav_count']
        read_only_fields = ['username', 'credit_score', 'is_verified']

    # 逻辑：通过反向查询统计数量
    def get_buy_count(self, obj):
        return obj.buy_orders.count() # 对应 Order 模型中的 buyer 关联

    def get_sell_count(self, obj):
        return obj.sell_orders.count() # 对应 Order 模型中的 seller 关联

    def get_fav_count(self, obj):
        # 对应 Favorite 模型
        from trade.models import Favorite
        return Favorite.objects.filter(user=obj).count()
    
    
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
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

# class ProductDetailSerializer(serializers.ModelSerializer):
#     # 嵌套显示卖家的详细信息
#     owner = UserInfoSerializer(read_only=True)
#     category_name = serializers.ReadOnlyField(source='category.name')

#     class Meta:
#         model = Product
#         fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    ''' 举报序列化器 '''
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['reporter', 'status']

class UserSerializer(serializers.ModelSerializer):
    ''' 用于在聊天中展示用户基本信息 '''
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
            'is_staff'  # 【核心新增】添加 Django 自带的管理员标记字段
        ]

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # 把用户信息加到返回的 JSON 里面
        data['username'] = self.user.username
        data['is_staff'] = self.user.is_staff
        data['id'] = self.user.id
        return data
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # DRF SimpleJWT 的标准做法是先调用父类的 validate
        # 它会自动处理 authenticate(用户名密码校验)
        
        username = attrs.get("username")
        user = User.objects.filter(username=username).first()
        
        if user and not user.is_active:
            raise serializers.ValidationError({
                "detail": "您的账号已被系统封禁，请联系管理员处理！"
            })

        # 执行标准验证（如果密码错，这里会抛出默认的 401 错误）
        data = super().validate(attrs)

        # 验证通过，获取token
        data['username'] = self.user.username
        data['id'] = self.user.id
        data['is_staff'] = self.user.is_staff          # 是否是运营客服（员工）
        data['is_superuser'] = self.user.is_superuser  # 【必须增加这一行】是否是超级管理员
        
        return data