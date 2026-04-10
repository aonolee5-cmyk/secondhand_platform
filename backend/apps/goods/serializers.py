from rest_framework import serializers
from .models import Category, Product
from .models import SensitiveWord



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    # 显示用户名
    owner_name = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    is_favorited = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('owner', 'status', 'create_time')
    
    def get_is_favorited(self, obj):
        from trade.models import Favorite
        user = self.context['request'].user
        if user.is_authenticated:
            # 查询当前用户是否收藏了当前商品
            return Favorite.objects.filter(user=user, product=obj).exists()
        return False
        
class SensitiveWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensitiveWord
        fields = '__all__'