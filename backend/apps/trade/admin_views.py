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
from rest_framework.permissions import IsAdminUser

# 订单管理与仲裁类
class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    企业级后台：全站订单管理与仲裁
    逻辑：只有进入 'arbitrating' 阶段的订单才允许管理员介入
    """
    queryset = Order.objects.all().order_by('-create_time')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser] 

    def get_queryset(self):
        """
        🚀 核心修正：
        1. 默认情况下，管理员列表只显示状态为 'arbitrating' (客服介入中) 的订单。
        2. 这种设计确保了买卖双方优先自行协商（dispute阶段），只有协商失败提请仲裁，后台才会受理。
        """
        status_filter = self.request.query_params.get('status')
        
        if status_filter:
            # 如果前端传了特定状态（如查看已关闭的单子），则按需过滤
            return Order.objects.filter(status=status_filter).order_by('-create_time')
        
        # 默认只看待处理的仲裁单
        return Order.objects.filter(status='arbitrating').order_by('-create_time')

    @action(detail=True, methods=['post'])
    def arbitrate(self, request, pk=None):
        """
        执行人工仲裁判决
        """
        order = self.get_object()
        decision = request.data.get('decision')
        
        # 只有在纠纷或仲裁中的单子才能执行判决
        if order.status not in ['dispute', 'arbitrating']:
            return Response({'detail': '该订单当前状态无需仲裁介入'}, status=400)

        if decision == 'refund':
            # 判决结果：全额退款给买家
            order.status = 'closed'
            order.save()
            # 商品回滚，重新进入市场
            p = order.product
            p.status = 'onsale'
            p.save()
            return Response({'detail': '仲裁成功：已判定退款，商品已重新上架'})
            
        elif decision == 'pay_seller':
            # 判决结果：强行打款给卖家（视为交易完成）
            order.status = 'received'
            order.save()
            return Response({'detail': '仲裁成功：已判定买家主张无效，货款已结算给卖家'})
            
        return Response({'detail': '无效指令'}, status=400)

# 数据大盘统计类
class AdminDashboardStatsView(APIView):
    """
    管理大盘数据接口（保持不变，已具备企业级聚合查询逻辑）
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