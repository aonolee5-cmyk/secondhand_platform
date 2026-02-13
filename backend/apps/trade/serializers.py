from rest_framework import serializers
from .models import CartItem, Order, Review
from goods.models import Product

class CartSerializer(serializers.ModelSerializer):
    # 额外显示商品信息，方便前端展示
    product_title = serializers.ReadOnlyField(source='product.title')
    product_price = serializers.ReadOnlyField(source='product.price')
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['user']

    def get_product_image(self, obj):
        if obj.product.images:
            return obj.product.images[0]
        return ""

class OrderSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='product.title')
    product_image = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_sn', 'buyer', 'seller', 'total_amount', 'status', 'pay_time']

    def get_product_image(self,obj):
        if obj.product.images and len(obj.product.images) > 0:
            return obj.product.images[0]
        return ""
    
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['order', 'create_time']