import time
import random
from django.db import transaction, models
from django.db.models import F, Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CartItem, Order, Review, Favorite
from .serializers import CartSerializer, OrderSerializer, ReviewSerializer, FavoriteSerializer
from goods.models import Product
from datetime import datetime
from users.services import CreditService
from rest_framework.exceptions import ValidationError 


class OrderViewSet(viewsets.ModelViewSet):
    """
    企业级订单视图集
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user)).order_by('-create_time')
    
    @transaction.atomic 
    def create(self, request, *args, **kwargs):
        """统一的下单逻辑"""
        user = request.user
        # 🚀 修正：对齐前端 Payload 的字段名 'product_id'
        product_id = request.data.get('product_id') 
        address_info = request.data.get('address') 

        if not product_id or not address_info:
            return Response({'detail': '商品ID和地址信息不能为空'}, status=400)

        try:
            # 锁定商品，防止并发
            product = Product.objects.select_for_update().get(id=product_id)
        except (Product.DoesNotExist, ValueError):
            return Response({'detail': '商品不存在'}, status=400)

        if product.status != 'onsale':
            return Response({'detail': '商品已被他人抢走或已下架'}, status=400)
        if product.owner == user:
            return Response({'detail': '不能购买自己的宝贝'}, status=400)

        # 生成唯一订单号
        order_sn = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{user.id}{random.randint(10,99)}"

        order = Order.objects.create(
            order_sn=order_sn,
            buyer=user,
            seller=product.owner,
            product=product,
            total_amount=product.price,
            receiver_info=address_info
        )

        # 修改状态为锁定
        product.status = 'locked'
        product.save()

        # 联动：清理购物车
        CartItem.objects.filter(user=user, product=product).delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """模拟支付"""
        order = self.get_object()
        if order.status != 'unpaid':
            return Response({'detail': '订单已处理，请勿重复支付'}, status=400)
        
        order.status = 'paid'
        order.pay_time = datetime.now()
        order.memo = f"ALIPAY_MOCK_{int(time.time())}"
        order.save()
        return Response({'status': '支付成功', 'order_sn': order.order_sn})

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """确认收货"""
        order = self.get_object()
        if order.buyer != request.user:
            return Response({'detail': '无权操作'}, status=403)
        if order.status not in ['paid', 'shipped']:
            return Response({'detail': '当前状态无法收货'}, status=400)
            
        order.status = 'received'
        order.save()
        # 信用分奖励
        CreditService.update_score(order.buyer, 3, '完成一笔交易', 'trade_done')
        return Response({'status': '已确认收货'})

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """卖家发货"""
        order = self.get_object()
        if order.seller != request.user:
            return Response({'detail': '无权操作'}, status=403)
        if order.status != 'paid':
            return Response({'detail': '订单未支付'}, status=400)
        order.status = 'shipped'
        order.save()
        return Response({'status': '发货成功'})

    @action(detail=True, methods=['post'])
    def apply_refund(self, request, pk=None):
        """申请退款"""
        order = self.get_object()
        reason = request.data.get('reason')
        order.status = 'dispute'
        order.refund_reason = reason
        order.save()
        return Response({'status': '退款申请已提交'})

    @action(detail=True, methods=['post'])
    def handle_refund(self, request, pk=None):
        """处理退款"""
        order = self.get_object()
        action_type = request.data.get('action')
        if action_type == 'agree':
            order.status = 'closed'
            order.save()
            order.product.status = 'onsale'
            order.product.save()
            return Response({'status': '已同意退款'})
        return Response({'status': '卖家已拒绝'})

    @action(detail=True, methods=['post'])
    def apply_arbitration(self, request, pk=None):
        """仲裁"""
        order = self.get_object()
        order.status = 'arbitrating'
        order.save()
        return Response({'status': '已提请仲裁'})


class ReviewViewSet(viewsets.ModelViewSet):
    """
    评价视图：逻辑已精简，统一使用 CreditService
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        order = serializer.validated_data.get('order')
        
        if order.buyer != self.request.user:
            raise ValidationError("你只能评价自己的订单")

        if order.status not in ['shipped', 'received', 'paid']:
            raise ValidationError("订单当前状态暂不能评价")

        # 1. 保存评价
        from django.db import IntegrityError
        try:
            review = serializer.save()
        except IntegrityError:
            raise ValidationError("该订单已评价")

        # 2. 🚀 买家评价加分
        CreditService.update_score(self.request.user, 4, '完成交易评价', 'review_done')
        
        # 3. 🚀 根据评分，给卖家加分或扣分 (逻辑完全交给 Service)
        seller = order.seller
        s = review.buyer_score
        if s == 5:
            CreditService.update_score(seller, 2, f"来自买家 {order.buyer.username} 的五星好评", "trade_done")
        elif s <= 2:
            CreditService.update_score(seller, -6, f"来自买家 {order.buyer.username} 的差评", "penalty")
        
        # 4. 自动结单
        if order.status != 'received':
            order.status = 'received'
            order.save()

    @action(detail=True, methods=['post'])
    def append_review(self, request, pk=None):
        review = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'detail': '内容不能为空'}, status=400)
        review.additional_comment = content
        review.additional_time = datetime.now()
        review.save()
        return Response({'status': '追加成功'})
    """
    评论视图
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic  # 确保评价存入和扣分操作要么同时成功，要么同时失败
    def perform_create(self, serializer):
        # 提取订单数据
        order = serializer.validated_data.get('order')
        
        # 安全性校验
        if order.buyer != self.request.user:
            raise ValidationError("非法操作：你只能评价自己购买的订单")

        # 业务状态校验
        if order.status not in ['shipped', 'received', 'paid']:
            raise ValidationError("订单尚未完成，暂不能评价")

        # 保存评价
        try:
            review = serializer.save()
        except IntegrityError:
            raise ValidationError("该订单已经评价过了，请勿重复提交")

        CreditService.update_score(self.request.user, 4, '完成交易评价', 'review_done')
        
        # 更新卖家信用分
        seller = order.seller
        if seller:
            s = review.buyer_score
            if s == 5:
                CreditService.update_score(seller, 2, f"来自买家 {order.buyer.username} 的五星好评", "trade_done")
            elif s == 1:
                CreditService.update_score(seller, -10, f"来自买家 {order.buyer.username} 的一星差评", "penalty")
        
        if order.status != 'received':
            order.status = 'received'
            order.save()
            
        score_change = 0
        s = review.buyer_score
        
        if s == 5: score_change = 2
        elif s == 4: score_change = 1
        elif s == 2: score_change = -5
        elif s == 1: score_change = -10
        
        if score_change != 0:
            seller.credit_score = F('credit_score') + score_change
            seller.save()

        
        #  更新订单状态为“已收货/已完成”
        if order.status != 'received':
            order.status = 'received'
            order.save()
        
        
    @action(detail=True, methods=['post'])
    def append_review(self, request, pk=None):
        """追加评价逻辑"""
        review = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response({'detail': '请输入追评内容'}, status=400)
        
        if review.additional_comment:
            return Response({'detail': '您已进行过追加评价'}, status=400)
            
        review.additional_comment = content
        review.additional_time = datetime.now()
        review.save()
        
        return Response({'status': '追加评价成功'})


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


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    收藏视图
    """
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 只看自己的收藏
        return Favorite.objects.filter(user=self.request.user).order_by('-add_time')
    
    def perform_create(self, serializer):
        # 自动关联当前用户
        serializer.save(user=self.request.user)
    
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': '缺少商品ID'}, status=400)
        
        # 查找是否存在记录
        fav = Favorite.objects.filter(user=request.user, product_id=product_id).first()
        
        if fav:
            fav.delete()
            return Response({'is_favorite': False, 'detail': '已取消收藏'})
        else:
            Favorite.objects.create(user=request.user, product_id=product_id)
            return Response({'is_favorite': True, 'detail': '已加入收藏夹'})


    @action(detail=False, methods=['get'])
    def check_status(self, request):
        product_id = request.query_params.get('product_id')
        exists = Favorite.objects.filter(user=request.user, product_id=product_id).exists()
        return Response({'is_favorite': exists})