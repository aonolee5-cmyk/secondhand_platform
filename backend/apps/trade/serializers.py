from rest_framework import serializers
from .models import CartItem, Order, Review,Favorite
from goods.models import Product
# from goods.serializers import ProductSerializer

class CartSerializer(serializers.ModelSerializer):
    # 额外显示商品信息
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
    has_review = serializers.SerializerMethodField() # 是否已首评
    has_additional = serializers.SerializerMethodField() # 是否已追评
    review_id = serializers.SerializerMethodField()
    product_title = serializers.ReadOnlyField(source='product.title')
    product_image = serializers.SerializerMethodField()
    buyer_name = serializers.ReadOnlyField(source='buyer.username')
    seller_name = serializers.ReadOnlyField(source='seller.username')
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_sn', 'buyer', 'seller', 'total_amount', 'status', 'pay_time' ,'refund_reason']

    def get_product_image(self,obj):
        if obj.product.images and len(obj.product.images) > 0:
            return obj.product.images[0]
        return ""
    
    def get_has_review(self, obj):
        return hasattr(obj, 'review')

    def get_has_additional(self, obj):
        if hasattr(obj, 'review'):
            return bool(obj.review.additional_comment)
        return False
    
    def get_review_id(self, obj):
        return obj.review.id if hasattr(obj, 'review') else None
    
class ReviewSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id', 'create_time']

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'images']
        
class FavoriteSerializer(serializers.ModelSerializer):
    # 使用本文件定义的 SimpleProductSerializer
    product_details = SimpleProductSerializer(source='product', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product', 'product_details', 'add_time']