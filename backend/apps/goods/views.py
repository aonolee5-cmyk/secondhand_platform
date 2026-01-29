from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.exceptions import ValidationError
from .utils import DFAFilter
from .models import SensitiveWord

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 发布商品时，自动关联当前登录用户
        serializer.save(owner=self.request.user)
        # title = self.request.data.get('title', '')
        # desc = self.request.data.get('desc', '')

    

def check_sensitive_words(content):
    """
    辅助函数：初始化 DFA 并检测
    """
    dfa = DFAFilter()
    # 从数据库加载所有敏感词
    words = SensitiveWord.objects.values_list('word', flat=True)
    for word in words:
        dfa.add(word)
    
    if dfa.contains_any(content):
        return True
    return False

# 修改 ProductViewSet 的 perform_create
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        """处理图片上传"""
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': '无文件'}, status=400)
        
        # 简单处理：直接保存到 media 文件夹并返回路径
        from django.core.files.storage import default_storage
        path = default_storage.save(f'products/{file_obj.name}', file_obj)
        return Response({'url': f'/media/{path}'})
    
    def perform_create(self, serializer):
        title = self.request.data.get('title', '')
        desc = self.request.data.get('desc', '')
        
        # 敏感词检测
        if check_sensitive_words(title + desc):
            raise ValidationError({'detail': '内容包含违禁词，请重新编辑后再发布！'})
        
        serializer.save(owner=self.request.user)