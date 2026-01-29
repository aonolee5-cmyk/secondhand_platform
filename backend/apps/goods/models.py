from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    """商品分类"""
    name = models.CharField(max_length=20, verbose_name="分类名称")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标类名") # 存 Element Plus 的图标名

    class Meta:
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Product(models.Model):
    """二手商品模型"""
    STATUS_CHOICES = (
        ('audit', '审核中'),
        ('onsale', '在售'),
        ('sold', '已售出'),
        ('off', '下架'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products", verbose_name="发布者")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="所属分类")
    
    title = models.CharField(max_length=100, verbose_name="商品标题")
    desc = models.TextField(verbose_name="详细描述")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    
    # 核心难点：JSONB 字段 (Django 4.2+ 的 JSONField 对应 PG 的 JSONB)
    # 用于存储：{'品牌': '苹果', '成色': '95新'} 等动态属性
    attributes = models.JSONField(default=dict, blank=True, verbose_name="动态属性")
    
    # 图片列表：存储图片路径列表
    images = models.JSONField(default=list, verbose_name="图片列表")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='audit')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "二手商品"
        verbose_name_plural = verbose_name

class SensitiveWord(models.Model):
    """敏感词库"""
    word = models.CharField(max_length=50, unique=True, verbose_name="敏感词")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "敏感词管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.word