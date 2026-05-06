from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Order
from goods.models import Product, Category

class AdminDashboardStatsView(APIView):
    """
    管理后台大盘统计接口，支持自定义时间范围查询，并自动执行时序数据补零逻辑
    """
    permission_classes = [IsAdminUser] 

    def get(self, request):
        # 解析日期范围参数
        start_str = request.query_params.get('start_date', '').strip()
        end_str = request.query_params.get('end_date', '').strip()

        try:
            if start_str and end_str and start_str != 'null':
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            else:
                # 默认展示近 7 天数据
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=6)
        except (ValueError, TypeError):
            return Response({'detail': '日期格式不合法，请输入 YYYY-MM-DD 格式'}, status=400)

        # 获取指定范围内的已支付订单数据集
        range_orders = Order.objects.filter(
            create_time__date__gte=start_date,
            create_time__date__lte=end_date,
            status='paid'
        )

        # 按日聚合交易金额
        db_data = (
            range_orders
            .annotate(day=TruncDay('create_time'))
            .values('day')
            .annotate(amount=Sum('total_amount'))
            .order_by('day')
        )

        # 构建日期映射字典，用于快速查找
        data_map = {res['day'].strftime('%Y-%m-%d'): float(res['amount']) for res in db_data}
        
        # 执行时序填充算法：确保时间轴连续，无数据日期自动补 0
        final_trend = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            final_trend.append({
                'day': date_str,
                'amount': data_map.get(date_str, 0)
            })
            current_date += timedelta(days=1)

        # 统计全局及核心业务指标
        total_gmv = range_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = range_orders.count()
        pending_audit = Product.objects.filter(status='audit').count()

        # 品类分布统计
        category_stats = list(
            Category.objects.annotate(prod_count=Count('product'))
            .values('name', 'prod_count')
        )

        # 统一响应格式
        return Response({
            'metrics': {
                'total_gmv': round(float(total_gmv), 2),
                'total_orders': total_orders,
                'pending_audit': pending_audit
            },
            'trend': final_trend,
            'categories': category_stats,
            'meta': {
                'start_date': str(start_date),
                'end_date': str(end_date),
                'data_points': len(final_trend)
            }
        })