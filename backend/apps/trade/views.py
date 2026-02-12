from django.shortcuts import render
import time, random
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CartItem, Order, Review
from .serializers import CartSerializer, OrderSerializer
from goods.models import Product
from django.db.models import F

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # 用户只能看到自己买的或卖的订单
        user = self.request.user
        return Order.objects.filter(models.Q(buyer=user) | models.Q(seller=user)).order_by('-create_time')

    @transaction.atomic # 开启事务
    def create(self, request, *args, **kwargs):
        """下单核心逻辑"""
        user = request.user
        product_id = request.data.get('product_id')
        address_info = request.data.get('address') # 前端传来的完整地址对象

        # 1. 锁定商品（悲观锁），防止并发冲突
        try:
            product = Product.objects.select_for_update().get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': '商品不存在'}, status=400)

        # 2. 检查状态
        if product.status != 'onsale':
            return Response({'detail': '商品已被他人抢走或已下架'}, status=400)
        if product.owner == user:
            return Response({'detail': '不能购买自己的商品'}, status=400)

        # 3. 生成订单号
        order_sn = f"{time.strftime('%Y%m%d%H%M%S')}{user.id}{random.randint(10,99)}"

        # 4. 创建订单记录
        order = Order.objects.create(
            order_sn=order_sn,
            buyer=user,
            seller=product.owner,
            product=product,
            total_amount=product.price,
            receiver_info=address_info
        )

        # 5. 修改商品状态为“锁定/交易中”
        product.status = 'locked'
        product.save()

        # 6. 如果是从购物车下单，删除购物车项
        CartItem.objects.filter(user=user, product=product).delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """支付管理：模拟支付"""
        order = self.get_object()
        if order.status != 'unpaid':
            return Response({'detail': '订单状态异常'}, status=400)
        
        # 模拟支付扣款逻辑...
        order.status = 'paid'
        order.pay_time = time.strftime('%Y-%m-%d %H:%M:%S')
        order.save()
        return Response({'status': '支付成功'})
    
    class ReviewViewSet(viewsets.ModelViewSet):
        queryset = Review.objects.all()
        serializer_class = ReviewSerializer
        permission_classes = [IsAuthenticated]

        def perform_create(self, serializer):
             # 1. 保存评价
            review = serializer.save()
        
            # 2. 核心逻辑：更新卖家信用分
            # 算法：5星+2分，4星+1分，3星不加，2星-5分，1星-10分
            order = review.order
            seller = order.seller
            score_change = 0
            
            s = review.buyer_score
            if s == 5: score_change = 2
            elif s == 4: score_change = 1
            elif s == 2: score_change = -5
            elif s == 1: score_change = -10
            
            if score_change != 0:
                seller.credit_score = F('credit_score') + score_change
                seller.save()
            
            # 3. 订单状态改为已完成（如果之前没改的话）
            order.status = 'received'
            order.save()