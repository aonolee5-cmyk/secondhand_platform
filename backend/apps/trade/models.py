from django.db import models
from django.contrib.auth import get_user_model
from goods.models import Product

User = get_user_model()

class CartItem(models.Model):
    """购物车模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name_plural= "购物车"
        db_table = "trade_cart"

class Order(models.Model):
    """订单模型"""
    ORDER_STATUS = (
        ('unpaid', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('received', '已收货'),
        ('closed', '已关闭'),
        ('dispute', '异常/纠纷'),
    )

    order_sn = models.CharField(max_length=50, unique=True, verbose_name="订单号")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buy_orders", verbose_name="买家")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sell_orders", verbose_name="卖家")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="商品")
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单金额")
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='unpaid', verbose_name="订单状态")
    
    # 收货信息快照（防止用户修改地址后影响旧订单）
    receiver_info = models.JSONField(default=dict, verbose_name="收货人信息")
    
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")

    class Meta:
        verbose_name_plural = "订单管理"
        db_table = "trade_order"

class Favorite(models.Model):
    """商品收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    add_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "商品收藏"
        unique_together = ('user', 'product') # 防止重复收藏
        

class Review(models.Model):
    """双方互评"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="review", verbose_name="订单")
    buyer_score = models.IntegerField(default=5, verbose_name="评分(1-5)")
    buyer_comment = models.TextField(verbose_name="评价内容")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "订单评价"