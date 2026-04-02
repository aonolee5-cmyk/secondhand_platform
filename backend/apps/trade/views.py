import time
import random
from django.db import transaction, models
from django.db.models import F, Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CartItem, Order, Review
from .serializers import CartSerializer, OrderSerializer, ReviewSerializer
from goods.models import Product

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        # 用户只能看到自己的订单
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user)).order_by('-create_time')
    
    @transaction.atomic 
    def create(self, request, *args, **kwargs):
        """下单逻辑"""
        user = request.user
        product_id = request.data.get('product_id')
        address_info = request.data.get('address') 

        if not product_id or not address_info:
            return Response({'detail': '商品id和地址信息不能为空'}, status=400)

        # 锁定商品，防止并发冲突
        try:
            product = Product.objects.select_for_update().get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': '商品不存在'}, status=400)

        # 检查状态
        if product.status != 'onsale':
            return Response({'detail': '商品已被他人抢走或已下架'}, status=400)
        if product.owner == user:
            return Response({'detail': '不能购买自己的商品'}, status=400)

        # 生成订单号
        order_sn = f"{time.strftime('%Y%m%d%H%M%S')}{user.id}{random.randint(10,99)}"

        # 创建订单记录
        order = Order.objects.create(
            order_sn=order_sn,
            buyer=user,
            seller=product.owner,
            product=product,
            total_amount=product.price,
            receiver_info=address_info
        )

        # 修改商品状态为锁定
        product.status = 'locked'
        product.save()

        # 如果是从购物车下单，删除购物车项
        CartItem.objects.filter(user=user, product=product).delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """支付管理：模拟支付"""
        order = self.get_object()
        if order.status != 'unpaid':
            return Response({'detail': '订单状态异常'}, status=400)
        
        # 模拟支付扣款逻辑
        order.status = 'paid'
        order.pay_time = time.strftime('%Y-%m-%d %H:%M:%S')
        order.save()
        return Response({'status': '支付成功'})
    
    # 退款
    @action(detail=True, methods=['post'])
    def apply_refund(self, request, pk=None):
        """买家申请退款/退货"""
        order = self.get_object()
        reason = request.data.get('reason')
        
        if order.buyer != request.user:
            return Response({'detail': '无权操作'}, status=403)
        if order.status not in['paid', 'shipped']:
            return Response({'detail': '当前状态无法申请退款'}, status=400)
            
        # 状态变更为纠纷
        order.status = 'dispute'
        order.refund_reason = reason
        order.save()
        return Response({'status': '已申请退款，等待卖家处理'})

    @action(detail=True, methods=['post'])
    def handle_refund(self, request, pk=None):
        """卖家处理退款申请"""
        order = self.get_object()
        action_type = request.data.get('action')
        
        if order.seller != request.user:
            return Response({'detail': '无权操作'}, status=403)
        if order.status != 'dispute':
            return Response({'detail': '该订单不在退款申请状态'}, status=400)
            
        if action_type == 'agree':
            # 卖家同意：订单关闭，商品回滚为在售状态
            order.status = 'closed'
            order.save()
            
            product = order.product
            product.status = 'onsale'
            product.save()
            return Response({'status': '已同意退款，金额将原路返回'})
            
        elif action_type == 'reject':
            return Response({'status': '卖家已拒绝,可申请客服介入'})

    
    @action(detail=True, methods=['post'])
    def apply_arbitration(self, request, pk=None):
        """客服介入"""
        order=self.get_object()
        if order.status != 'dispute':
            return Response({'detail': '订单未处于纠纷'}, status=400)
        order.status = 'arbitrating'
        order.save()
        return Response({'status': '已申请客服介入，请等待平台进行处理'})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 保存评价
        review = serializer.save()
    
        # 核心逻辑：更新卖家信用分
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
            seller.refresh_from_db() 
        
        # 订单状态改为已完成
        order.status = 'received'
        order.save()


class CartViewSet(viewsets.ModelViewSet):
    ''' 购物车视图集 '''
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 只返回当前登录用户的购物车数据
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 防止重复添加同一个商品
        product = serializer.validated_data['product']
        if CartItem.objects.filter(user=self.request.user, product=product).exists():
            raise serializers.ValidationError("该商品已在购物车中")
        serializer.save(user=self.request.user)