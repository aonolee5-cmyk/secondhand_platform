# from backend.apps.trade.serializers import OrderSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.exceptions import ValidationError
from .utils import DFAFilter
from .models import SensitiveWord
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework import permissions
from django.db.models import Q
from django.core.files.storage import default_storage
from rest_framework.permissions import AllowAny

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
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
            # 如果是管理员(Staff)，拥有上帝视角，可以看到所有状态、所有人的商品
            qs = Product.objects.all()
        elif user.is_authenticated and query_params.get('mine') == '1':
            # 普通用户看“我的发布”
            qs = Product.objects.filter(owner=user)
        else:
            # 游客或普通看大厅，只能看到“在售”
            qs = Product.objects.filter(status='onsale')

        # 2. 手动叠加搜索过滤
        search_kw = query_params.get('search', None)
        if search_kw:
            # print(f">>> 后端正在搜索: {search_kw}")
            qs = qs.filter(
                Q(title__icontains=search_kw) | Q(desc__icontains=search_kw)
            )

        # 3. 手动叠加分类过滤
        cat_id = query_params.get('category', None)
        if cat_id:
            qs = qs.filter(category_id=cat_id)

        status_filter = query_params.get('status', None)
        if status_filter and user.is_staff:
            qs = qs.filter(status=status_filter)
        
        return qs.order_by('-create_time')

    def perform_update(self, serializer):
        # 🚀 核心防护：获取数据库中【当前】的商品对象
        instance = self.get_object()
        user = self.request.user

        # 如果商品已经是封禁状态，且不是管理员在操作
        if instance.status == 'banned' and not user.is_staff:
            raise ValidationError({'detail': '该商品已被管理员封禁，无法进行操作！'})

        if instance.staus == 'audit' and user.is_staff:
           raise ValidationError({'detail': '该商品正在审核中，请勿重复操作！如需修改请先撤回申请。'}) 
         
        
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
        new_status = request.data.get('status')
        user = request.user
        
        if product.status == 'banned' and not user.is_staff:
            return Response({'detail': '商品已被强制下架，无法操作'}, status=403)
        
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
            return Response({'detail': '状态更新成功', 'current_status': product.status})
        
        return Response({'detail': '无效的状态值'}, status=403)

    @action(detail=True, methods=['post'])
    def force_takedown(self, request, pk=None):
        '''
        强制下架（处理在售，被举报并被证实的违规商品）
        '''
        product = self.get_object()
        user = request.user
        reason = request.data.get('reason', '经核实，该商品违反平台交易守则')

        # 只有 Staff (运营客服) 和 Admin 才能执行
        if not user.is_staff:
            return Response({'detail': '权限不足，无法执行治理操作'}, status=403)

        # 强制将状态转为 banned (封禁)
        product.status = 'banned'
        # 在商品描述前追加封禁理由，作为“存证”
        product.desc = f"【系统禁售提示：{reason}】\n" + product.desc
        product.save()

        # 可以在这里增加其他联动逻辑，比如：扣除卖家信用分
        seller = product.owner
        seller.credit_score -= 10
        seller.save()

        return Response({
            'detail': '商品已执行强制下架，并已扣除卖家信用分',
            'current_status': 'banned'
        })
    
    # 发布逻辑，增加敏感词检测
    def perform_create(self, serializer):
        title = self.request.data.get('title', '')
        desc = self.request.data.get('desc', '')
        
        # 调用敏感词检测函数
        if check_sensitive_words(title + desc):
            raise ValidationError({'detail': '内容包含违禁词，请重新编辑后再发布！'})
        
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # 如果是 'list' (列表页) 或 'retrieve' (详情页)，允许所有人访问
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        # 其他操作（如发布宝贝、修改、删除），必须登录
        return [permissions.IsAuthenticated()]
# 敏感词检测    
def check_sensitive_words(content):
    dfa = DFAFilter()
    words = SensitiveWord.objects.values_list('word', flat=True)
    for word in words:
        dfa.add(word)
    return dfa.contains_any(content)

    