from django.contrib import admin
from .models import Category, Product
from .models import Category, Product, SensitiveWord

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon') # 后台列表显示哪些列

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 后台列表显示的字段
    list_display = ('title', 'owner', 'price', 'category', 'status', 'create_time')
    # 右侧过滤器
    list_filter = ('status', 'category')
    # 搜索框
    search_fields = ('title', 'desc')
    # 可以在列表页直接编辑的字段
    list_editable = ('status', 'price')
    
@admin.register(SensitiveWord)
class SensitiveWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'create_time')