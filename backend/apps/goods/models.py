from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex

User = get_user_model()

class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=20, verbose_name="分类名称")
    
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标类名")

    attribute_fields = models.JSONField(default=list, blank=True, verbose_name="扩展属性")
    
    
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Product(models.Model):
    """二手物品模型"""
    STATUS_CHOICES = (
        ('audit', '审核中'),
        ('onsale', '在售'),
        ('sold', '已售出'),
        ('off', '下架'),
        ('banned','违规下架')
    )
    browse_count = models.PositiveIntegerField(default=0, verbose_name="浏览次数")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products", verbose_name="发布者")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True,verbose_name="所属分类")
    
    title = models.CharField(max_length=100, verbose_name="商品标题")
    desc = models.TextField(verbose_name="详细描述")
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True, verbose_name="价格")
    
    # 使用jsonb字段来存储商品的动态属性
    attributes = models.JSONField(default=dict, blank=True, verbose_name="动态属性")
    
    images = models.JSONField(default=list, verbose_name="图片列表")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, db_index=True, default='audit')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "二手物品"
        verbose_name_plural = verbose_name
        indexes = [
            GinIndex(fields=['attributes'], name='idx_product_attrs_gin')
        ]

class SensitiveWord(models.Model):
    """敏感词库"""
    word = models.CharField(max_length=50, unique=True, verbose_name="敏感词")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "敏感词管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.word


class BrowsingHistory(models.Model):
    """浏览记录模型"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name="用户")
    product = models.ForeignKey('goods.Product', on_delete=models.CASCADE, verbose_name="商品")
    viewed_time = models.DateTimeField(auto_now=True, verbose_name="最后浏览时间")

    class Meta:
        verbose_name = "浏览记录"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'product')
        ordering = ['-viewed_time']