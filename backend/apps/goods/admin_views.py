from rest_framework import viewsets, permissions
from .models import Product, SensitiveWord
from .serializers import ProductSerializer, SensitiveWordSerializer 
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, filters
from users.permissions import IsOperationalManager, IsSystemAdmin


class AdminProductViewSet(viewsets.ModelViewSet):
    """
    商品管理：审核、强行下架
    """
    queryset = Product.objects.all().order_by('-create_time')
    serializer_class = ProductSerializer
    permission_classes = [IsOperationalManager]

    # 自定义过滤：只看待审核商品
    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status:
            return self.queryset.filter(status=status)
        return self.queryset

    @action(detail=True, methods=['post'])
    def audit(self, request, pk=None):
        product = self.get_object()
        is_pass = request.data.get('pass') # 前端传布尔值
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
    search_fields = ['word'] # 支持前端搜索