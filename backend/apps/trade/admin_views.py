# backend/apps/trade/admin_views.py
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from .models import Order
from goods.models import Product, Category
from .serializers import OrderSerializer

# 1. 之前漏掉或命名不一致的：订单管理与仲裁类
class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    企业级后台：全站订单管理与仲裁
    """
    queryset = Order.objects.all().order_by('-create_time')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser] 

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @action(detail=True, methods=['post'])
    def arbitrate(self, request, pk=None):
        order = self.get_object()
        decision = request.data.get('decision')
        if order.status not in ['dispute', 'arbitrating']:
            return Response({'detail': '订单未处于纠纷状态'}, status=400)

        if decision == 'refund':
            order.status = 'closed'
            order.save()
            p = order.product
            p.status = 'onsale'
            p.save()
            return Response({'detail': '仲裁成功：已退款并重新上架'})
        elif decision == 'pay_seller':
            order.status = 'received'
            order.save()
            return Response({'detail': '仲裁成功：已打款给卖家'})
        return Response({'detail': '无效指令'}, status=400)

# 2. 数据大盘统计类
class AdminDashboardStatsView(APIView):
    """
    企业级管理大盘数据接口
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)

        total_gmv = Order.objects.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = Order.objects.count()
        pending_audit = Product.objects.filter(status='audit').count()

        trend_qs = (
            Order.objects.filter(create_time__date__gte=seven_days_ago)
            .annotate(day=TruncDay('create_time'))
            .values('day')
            .annotate(amount=Sum('total_amount'), count=Count('id'))
            .order_by('day')
        )
        
        trend = []
        for entry in trend_qs:
            trend.append({
                'day': entry['day'].strftime('%Y-%m-%d'),
                'amount': float(entry['amount']),
                'count': entry['count']
            })

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
            'trend': trend,
            'categories': list(category_stats)
        })