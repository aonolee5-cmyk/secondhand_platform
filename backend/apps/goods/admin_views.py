from rest_framework import viewsets, permissions
from .models import Product, SensitiveWord, Category
from .serializers import ProductSerializer, SensitiveWordSerializer, CategorySerializer 
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, filters
from users.permissions import IsOperationalManager, IsSystemAdmin


class AdminProductViewSet(viewsets.ModelViewSet):
    """
    审核、强行下架
    """
    queryset = Product.objects.all().order_by('-create_time')
    serializer_class = ProductSerializer
    permission_classes = [IsOperationalManager]

    # 只看待审核商品
    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status:
            return self.queryset.filter(status=status)
        return self.queryset

    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        product = self.get_object()
        is_pass = request.data.get('pass') 
        product.status = 'onsale' if is_pass else 'off'
        product.save()
        return Response({'detail': '审核处理完成'})
    
class AdminSensitiveWordViewSet(viewsets.ModelViewSet):
    """
    敏感词库
    """
    queryset = SensitiveWord.objects.all().order_by('-create_time')
    serializer_class = SensitiveWordSerializer 
    permission_classes = [IsSystemAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['word']
    
class AdminCategoryViewSet(viewsets.ModelViewSet):
    """
    分类及动态属性管理
    """
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [IsSystemAdmin]