# backend/apps/trade/analytics_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from .models import Order
from goods.models import Product, Category

class AdminDashboardStatsView(APIView):
    """
    企业级管理大盘数据接口
    """
    # 仅管理员可访问（需配合自定义权限类）
    # permission_classes = [IsAdminUser] 

    def get(self, request):
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)

        # 1. 核心指标统计 (Key Metrics)
        total_gmv = Order.objects.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = Order.objects.count()
        pending_audit = Product.objects.filter(status='audit').count()

        # 2. 交易趋势图数据 (近7日)
        trend_data = (
            Order.objects.filter(create_time__date__gte=seven_days_ago)
            .annotate(day=TruncDay('create_time'))
            .values('day')
            .annotate(amount=Sum('total_amount'), count=Count('id'))
            .order_by('day')
        )

        # 3. 品类占比统计 (Pie Chart)
        category_stats = (
            Category.objects.annotate(prod_count=Count('product'))
            .values('name', 'prod_count')
        )

        return Response({
            'metrics': {
                'total_gmv': float(total_gmv),
                'total_orders': total_orders,
                'pending_audit': pending_audit
            },
            'trend': trend_data,
            'categories': category_stats
        })