from django.contrib import admin
from .models import Category, Product
from .models import Category, Product, SensitiveWord

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon') # 后台列表显示的列

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 后台列表显示的字段
    list_display = ('title', 'owner', 'price', 'category', 'status', 'create_time')
    list_filter = ('status', 'category')
    search_fields = ('title', 'desc')
    list_editable = ('status', 'price')
    
@admin.register(SensitiveWord)
class SensitiveWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'create_time')