from rest_framework import serializers
from .models import Category, Product
from .models import SensitiveWord
from .models import BrowsingHistory
from users.models import Report

class ProductReportSerializer(serializers.ModelSerializer):
    """专门用于审核页展示的简易举报序列化器"""
    reporter_name = serializers.ReadOnlyField(source='reporter.username')
    
    class Meta:
        model = Report
        fields = ['reporter_name', 'reason', 'content', 'create_time', 'status']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'attribute_fields']

class ProductSerializer(serializers.ModelSerializer):
    # 显示用户名
    owner_name = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    is_favorited = serializers.SerializerMethodField()
    reports = ProductReportSerializer(many=True, read_only=True, source='report_set') 
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('owner', 'status', 'create_time', 'browse_count')
    
    def get_is_favorited(self, obj):
        from trade.models import Favorite
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, product=obj).exists()
        return False
        
class SensitiveWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensitiveWord
        fields = '__all__'

class BrowsingHistorySerializer(serializers.ModelSerializer):
    """
    浏览记录序列化器
    """
    product_title = serializers.ReadOnlyField(source='product.title')
    product_price = serializers.ReadOnlyField(source='product.price')
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = BrowsingHistory
        fields = ['id', 'product', 'product_title', 'product_price', 'product_image', 'viewed_time']

    def get_product_image(self, obj):
        if obj.product.images and len(obj.product.images) > 0:
            return obj.product.images[0]
        return ""