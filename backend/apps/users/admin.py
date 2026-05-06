from django.contrib import admin
from .models import User, Report
from .services import CreditService 
from .models import CreditLog


@admin.register(User)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'real_name', 'verify_status', 'is_verified', 'credit_score')
    list_filter = ('verify_status', 'is_verified')
    list_editable = ('verify_status', 'credit_score')
    search_fields = ('username', 'real_name',)
    
    actions = ['approve_verification']
    
    @admin.action(description='审核通过选中的用户实名认证')
    def approve_verification(self, request, queryset):
        success_count = 0
        for user in queryset:
            # 只有从 非通过状态 变更为 通过状态时，才触发加分
            if user.verify_status != 2:
                user.verify_status = 2
                user.is_verified = True
                user.save()
                
                # 调用服务类执行加分并记录日志
                CreditService.update_score(user, 10, "完成实名认证加分", "verify")
                success_count += 1
                
        self.message_user(request, f'成功通过 {success_count} 个用户的实名认证，信用分已更新。')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'target_user', 'reason', 'status', 'create_time')
    list_filter = ('status', 'reason')
    actions = ['mark_as_processed']

    @admin.action(description="核实举报：已处理并执行扣分")
    def mark_as_processed(self, request, queryset):
        processed_count = 0
        for report in queryset:
            if report.status == 0: # 只处理待处理的单子
                if report.product:
                    product = report.product
                    if product.status != 'banned':
                        product.status = 'banned'
                        product.desc = f"【系统禁售提示：基于举报单 #{report.id} 核实封禁】\n" + product.desc
                        product.save()
                target_user = report.target_user
                
                # 调用服务类扣除 6 分
                CreditService.update_score(target_user, -6, "商品违规被举报核实", "penalty")
                
                report.status = 1 # 标记为已处理
                report.save()
                processed_count += 1
                
        self.message_user(request, f"成功处理 {processed_count} 条举报，违规用户已被扣除 6 分信用分，相关商品已被下架。")

@admin.register(CreditLog)
class CreditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'action_type', 'create_time')
    list_filter = ('action_type',)