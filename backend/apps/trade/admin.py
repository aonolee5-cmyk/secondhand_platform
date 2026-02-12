from django.contrib import admin
from django.contrib import admin
from .models import CartItem, Order

admin.site.register(CartItem)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_sn', 'buyer', 'seller', 'product', 'total_amount', 'status')
    list_filter = ('status',)