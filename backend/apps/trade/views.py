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

class OrderViewSet(viewsets.ModelViewSet):
    """
    订单视图
    """
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
            return Response({'detail': '订单已完成，请勿重复支付！'}, status=400)
        
        # 模拟支付扣款逻辑
        order.status = 'paid'
        order.pay_time = datetime.now()
        order.memo = f"ALIPAY_TRADE_{int(time.time())}"
        order.save()
        return Response({'status': '支付成功',
                         'order_sn': order.order_sn,
                         'pay_no': order.memo                         
                         })
    
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
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """买家确认收货"""
        order = self.get_object()
        
        # 安全检查：只有买家能点收货
        if order.buyer != request.user:
            return Response({'detail': '无权操作'}, status=403)
        
        # 逻辑检查：只有已发货（shipped）或已支付（paid，防止卖家忘了点发货）的订单能收货
        if order.status not in ['paid', 'shipped']:
            return Response({'detail': '当前订单状态无需确认收货'}, status=400)
            
        # 变更状态为交易完成
        order.status = 'received'
        order.save()
        
        return Response({'status': '已确认收货，交易完成'})
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """卖家执行发货"""
        order = self.get_object()
        
        # 🛡️ 安全检查：只有卖家本人能点发货
        if order.seller != request.user:
            return Response({'detail': '非法操作：您不是该订单的卖家'}, status=403)
        
        # 🛡️ 状态检查：只有“已支付”的订单才能发货
        if order.status != 'paid':
            return Response({'detail': '订单状态异常，无法发货'}, status=400)
            
        # 变更状态为已发货
        order.status = 'shipped'
        order.save()
        
        return Response({'status': '发货成功，已通知买家'})
    
class ReviewViewSet(viewsets.ModelViewSet):
    """
    评论视图
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic  # 🚀 亮点1：开启事务，确保评价存入和扣分操作要么同时成功，要么同时失败
    def perform_create(self, serializer):
        # 1. 提取订单数据
        order = serializer.validated_data.get('order')
        
        # 🛡️ 亮点2：安全性校验（越权检查）
        # 必须确保：当前登录的用户 是 订单的买家，否则任何人都能随便给别人评价
        if order.buyer != self.request.user:
            raise ValidationError("非法操作：你只能评价自己购买的订单")

        # 🛡️ 亮点3：业务状态校验
        # 只有“已发货”或“已收货”的订单才能评价（防止恶意对未支付订单刷分）
        if order.status not in ['shipped', 'received', 'paid']:
            raise ValidationError("订单尚未完成，暂不能评价")

        # 2. 保存评价
        # 增加异常捕获，防止因为 OneToOneField 重复评价导致系统崩溃
        try:
            review = serializer.save()
        except IntegrityError:
            raise ValidationError("该订单已经评价过了，请勿重复提交")

        # 3. 核心逻辑：更新卖家信用分
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
            # 💡 提示：使用 F 对象后，seller.credit_score 在当前内存里还是旧值
            # 如果后面还需要用到最新分值，必须执行下一行：
            # seller.refresh_from_db() 
        
        # 4. 更新订单状态为“已收货/已完成”
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
        # 只看自己的收藏，并按时间倒序
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
            # 如果已存在，则删除（取消收藏）
            fav.delete()
            return Response({'is_favorite': False, 'detail': '已取消收藏'})
        else:
            # 如果不存在，则创建（加入收藏）
            Favorite.objects.create(user=request.user, product_id=product_id)
            return Response({'is_favorite': True, 'detail': '已加入收藏夹'})

    # 🚀 亮点功能：进入商品页时查询状态
    @action(detail=False, methods=['get'])
    def check_status(self, request):
        product_id = request.query_params.get('product_id')
        exists = Favorite.objects.filter(user=request.user, product_id=product_id).exists()
        return Response({'is_favorite': exists})