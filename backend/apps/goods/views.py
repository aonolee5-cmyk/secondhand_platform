# from backend.apps.trade.serializers import OrderSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product,SensitiveWord, BrowsingHistory
from .serializers import CategorySerializer, ProductSerializer, BrowsingHistorySerializer
from rest_framework.exceptions import ValidationError
from .utils import DFAFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework import permissions
from django.db.models import Q
from django.core.files.storage import default_storage
from rest_framework.permissions import AllowAny
from users.services import CreditService


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('owner', 'category').all()
    serializer_class = ProductSerializer
    # 设置游客只读，登录可操作
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'desc']
    filterset_fields = {'category':['exact'],
                        'price':['gte', 'lte'],
    }

    ordering_fields = ['price', 'create_time', 'browse_count']
    ordering = ['-create_time']
    def get_queryset(self):
        """
        商品列表查询集
        """
        user = self.request.user
        query_params = self.request.query_params
        
        if self.action in ['retrieve', 'change_status', 'update', 'partial_update', 'destroy', 'force_takedown']:
            return Product.objects.all()
        
        if user.is_authenticated and user.is_staff:
            qs = Product.objects.all()
        elif user.is_authenticated and query_params.get('mine') == '1':
            qs = Product.objects.filter(owner=user)
        else:
            qs = Product.objects.filter(status='onsale')

        search_kw = query_params.get('search', None)
        if search_kw:
            qs = qs.filter(
                Q(title__icontains=search_kw) | Q(desc__icontains=search_kw)
            )

        cat_id = query_params.get('category', None)
        if cat_id:
            qs = qs.filter(category_id=cat_id)

        status_filter = query_params.get('status', None)
        if status_filter and user.is_staff:
            qs = qs.filter(status=status_filter)
        
        return qs.order_by('-create_time')
    
    def create(self, request, *args, **kwargs):
        print("--- 收到发布请求数据 ---")
        print(request.data)
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("--- 商品发布验证失败详情 ---")
            print(serializer.errors) 
            print("-------------------------")
            
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user

        if instance.status == 'banned' and not user.is_staff:
            raise ValidationError({'detail': '该物品已被封禁，无法进行操作！'})

        if instance.staus == 'audit' and user.is_staff:
           raise ValidationError({'detail': '审核中，请勿重复操作！如需修改请先撤回申请。'}) 
         
        
        if not user.is_staff:
            serializer.save(owner=user, status='audit')
        else:
            serializer.save()
    
    # 上传图片
    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': '无文件'}, status=400)
        path = default_storage.save(f'products/{file_obj.name}', file_obj)
        return Response({'url': f'/media/{path}'})

    # 下架/上架切换
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        product = self.get_object()
        old_status = product.status
        new_status = request.data.get('status')
        user = request.user
        
        if product.status == 'banned' and not user.is_staff:
            return Response({'detail': '物品已被强制下架，无法操作'}, status=403)
        
        if not user.is_staff:
            if new_status not in ['onsale', 'off']:
                return Response({'detail': '无权切换至该状态'}, status=403)
            
            # 普通用户上架，强制进入审核态
            if new_status == 'onsale':
                new_status = 'audit'

        valid_statuses = [choice[0] for choice in Product.STATUS_CHOICES]
        if new_status in valid_statuses:
            product.status = new_status
            product.save()
            
            if user.is_staff and old_status == 'audit' and new_status == 'onsale':
                CreditService.update_score(
                    product.owner, 
                    3,
                    f'审核通过：{product.title}',
                    'post_product')
            return Response({'detail': '状态更新成功', 'current_status': product.status})
        
        return Response({'detail': '无效的状态值'}, status=403)

    @action(detail=True, methods=['post'])
    def force_takedown(self, request, pk=None):
        '''
        强制下架
        '''
        product = self.get_object()
        user = request.user
        reason = request.data.get('reason', '经核实，该物品违反平台交易守则')

        # 只有 Staff  和 Admin 才能执行
        if not user.is_staff:
            return Response({'detail': '权限不足，无法执行治理操作'}, status=403)

        if product.status !='banned':
           product.status = 'banned'
           product.desc = f'该商品因违规被管理员强制下架，原因：{reason}\n' + product.desc
           product.save()

        return Response({
            'detail': '商品已被强制下架',
            'current_status': 'banned'
        })
    
    # 发布逻辑，增加敏感词检测
    def perform_create(self, serializer):
        title = self.request.data.get('title', '')
        desc = self.request.data.get('desc', '')
        
        if check_sensitive_words(title + desc):
            raise ValidationError({'detail': '内容包含违禁词，请重新编辑后再发布！'})
        
        serializer.save(owner=self.request.user)
        CreditService.update_score(
            self.request.user,
            3,
            f'发布商品：{title}',
            'post_product'
        )
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

class BrowsingHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BrowsingHistorySerializer # 稍后在serializers定义

    def get_queryset(self):
        return BrowsingHistory.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def record(self, request):
        product_id = request.data.get('product_id')
        BrowsingHistory.objects.update_or_create(
            user=request.user,
            product_id=product_id
        )
        return Response({'status': 'recorded'})

    @action(detail=False, methods=['post'])
    def clear_all(self, request):
        """清空所有记录"""
        self.get_queryset().delete()
        return Response({'status': 'cleared'})

# 敏感词检测    
def check_sensitive_words(content):
    dfa = DFAFilter()
    words = SensitiveWord.objects.values_list('word', flat=True)
    for word in words:
        dfa.add(word)
    return dfa.contains_any(content)

    