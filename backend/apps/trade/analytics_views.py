# backend/apps/trade/analytics_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from .models import Order
from goods.models import Product, Category

class AdminDashboardStatsView(APIView):
    """
    企业级管理大盘数据接口：支持动态日期范围分析
    """
    # 建议取消注释以确保安全
    # from rest_framework.permissions import IsAdminUser
    # permission_classes = [IsAdminUser] 

    def get(self, request):
        # 1. 🚀 获取并解析前端传来的日期参数
        start_str = request.query_params.get('start_date')
        end_str = request.query_params.get('end_date')

        try:
            if start_str and end_str:
                # 解析前端传来的 YYYY-MM-DD 格式
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            else:
                # 默认逻辑：显示最近 7 天（包含今天）
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=6)
        except ValueError:
            return Response({'detail': '日期格式错误，请使用 YYYY-MM-DD'}, status=400)

        # 2. 🚀 构建核心过滤查询集 (Base Queryset)
        # 我们只统计指定日期范围内产生的订单
        range_orders = Order.objects.filter(create_time__date__range=[start_date, end_date])

        # 3. 核心指标统计 (Key Metrics)
        # 总成交额仅计算已支付的订单
        total_gmv = range_orders.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = range_orders.count()
        # 待审核商品是全局属性，不随日期变动，方便管理员随时处理
        pending_audit = Product.objects.filter(status='audit').count()

        # 4. 交易趋势图数据 (Trend Data)
        # 按天聚合，统计每天的成交总额和订单量
        trend_data = (
            range_orders
            .annotate(day=TruncDay('create_time'))
            .values('day')
            .annotate(amount=Sum('total_amount'), count=Count('id'))
            .order_by('day')
        )

        # 5. 品类占比统计 (Pie Chart)
        # 亮点逻辑：统计在该时间段内“卖得最好”的品类分布
        category_stats = (
            Category.objects.annotate(
                prod_count=Count(
                    'product', 
                    filter=Q(product__order__in=range_orders.filter(status='paid'))
                )
            ).values('name', 'prod_count')
        )

        # 6. 响应数据组装
        return Response({
            'metrics': {
                'total_gmv': float(total_gmv),
                'total_orders': total_orders,
                'pending_audit': pending_audit,
                'start_date': start_date, # 返回确认的日期给前端
                'end_date': end_date
            },
            'trend': trend_data,
            'categories': category_stats
        })