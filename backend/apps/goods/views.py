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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # 💡 权限：游客只读，登录可操作
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        自定义商品列表查询集，支持“我的商品”与“大厅商品”切换，
        """
        user = self.request.user
        action_name = self.action
        query_params = self.request.query_params
        
        # 1. 基础逻辑：是看“我的”还是看“大厅”的
        is_mine = query_params.get('mine') == '1'
        if user.is_authenticated and (action_name == 'change_status' or is_mine):
            qs = Product.objects.filter(owner=user)
        else:
            qs = Product.objects.filter(status='onsale')

        # 2. 手动叠加搜索过滤 (search 参数)
        search_kw = query_params.get('search', None)
        if search_kw:
            print(f">>> 后端正在搜索: {search_kw}")
            qs = qs.filter(
                Q(title__icontains=search_kw) | Q(desc__icontains=search_kw)
            )

        # 3. 手动叠加分类过滤 (category 参数)
        cat_id = query_params.get('category', None)
        if cat_id:
            qs = qs.filter(category_id=cat_id)

        return qs.order_by('-create_time')
    def get_serializer_class(self):
        '''如果是列表视图，使用简化的序列化器；如果是详情视图，使用完整的序列化器'''
        return ProductSerializer
    
    def get_permissions(self):
        """
        动态设置权限，
        """
        if self.action in ['update', 'partial_update', 'destroy', 'change_status']:
            return [IsAuthenticated()]
        return [AllowAny()]

        # 💡 动作1：上传图片
    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': '无文件'}, status=400)
        path = default_storage.save(f'products/{file_obj.name}', file_obj)
        return Response({'url': f'/media/{path}'})

    # 💡 动作2：下架/上架切换
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        product = self.get_object()
        new_status = request.data.get('status')
        if new_status in ['onsale', 'off', 'sold']:
            product.status = new_status
            product.save()
            return Response({'status': 'success'})
        return Response({'error': '状态非法'}, status=400)

    # 💡 核心：重写发布逻辑，增加敏感词检测
    def perform_create(self, serializer):
        title = self.request.data.get('title', '')
        desc = self.request.data.get('desc', '')
        
        # 调用下面定义的敏感词检测函数
        if check_sensitive_words(title + desc):
            raise ValidationError({'detail': '内容包含违禁词，请重新编辑后再发布！'})
        
        serializer.save(owner=self.request.user)

# --- 工具函数保持在类外面 ---
def check_sensitive_words(content):
    dfa = DFAFilter()
    words = SensitiveWord.objects.values_list('word', flat=True)
    for word in words:
        dfa.add(word)
    return dfa.contains_any(content)