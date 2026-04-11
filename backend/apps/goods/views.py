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

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(status='onsale')
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
        # action_name = self.action
        query_params = self.request.query_params
        
        # 1. 基础逻辑：是看“我的”还是看“大厅”的
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
            print(f">>> 后端正在搜索: {search_kw}")
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
        if new_status in ['onsale', 'off', 'sold', 'audit']:
            product.status = new_status
            product.save()
            return Response({'status': 'success'})
        return Response({'error': '状态非法'}, status=400)

    # 发布逻辑，增加敏感词检测
    def perform_create(self, serializer):
        title = self.request.data.get('title', '')
        desc = self.request.data.get('desc', '')
        
        # 调用敏感词检测函数
        if check_sensitive_words(title + desc):
            raise ValidationError({'detail': '内容包含违禁词，请重新编辑后再发布！'})
        
        serializer.save(owner=self.request.user)

def check_sensitive_words(content):
    dfa = DFAFilter()
    words = SensitiveWord.objects.values_list('word', flat=True)
    for word in words:
        dfa.add(word)
    return dfa.contains_any(content)