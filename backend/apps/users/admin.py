from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 注册自定义用户模型，这样 admin 后台就能管理用户了
# admin.site.register(User, UserAdmin)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'real_name', 'verify_status', 'is_verified', 'credit_score')
    list_filter = ('verify_status',)
    # 2. 允许在列表页直接编辑的字段
    list_editable = ('verify_status', 'credit_score')
    # 4. 搜索框
    search_fields = ('username', 'real_name',)
    actions = ['approve_verification']
    
    def approve_verification(self, request, queryset):
        rows_updated = queryset.update(verify_status=2, is_verified=True)
        self.message_user(request, f'已通过 {rows_updated} 个用户的实名认证')
    
    approve_verification.short_description = '审核通过选中的用户实名认证'