from django.contrib import admin
from django.contrib import admin
from .models import CartItem, Order

admin.site.register(CartItem)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_sn', 'buyer', 'seller', 'product', 'total_amount', 'status')
    list_filter = ('status',)
    actions = ['close_order_by_admin']
    
    @admin.action(description='客服介入完成并关闭订单')
    def close_order_by_admin(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, '客服介入完成并关闭了订单')