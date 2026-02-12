from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Report

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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'target_user', 'reason', 'status', 'create_time')
    list_filter = ('status', 'reason')
    actions = ['mark_as_processed']

    @admin.action(description="标记为已处理并扣除被举报人信用分")
    def mark_as_processed(self, request, queryset):
        for report in queryset:
            if report.status == 0:
                # 惩罚逻辑：一旦核实举报，扣除被举报人 10 分信用
                user = report.target_user
                user.credit_score -= 10
                user.save()
                report.status = 1
                report.save()
        self.message_user(request, "举报已处理，相关用户已被扣分处罚")