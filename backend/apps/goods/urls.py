from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet

# 1. 创建一个路由器实例
router = DefaultRouter()

# 2. 注册我们的 ViewSets
# 这样会自动生成 /api/goods/categories/ 和 /api/goods/list/ 的各种增删改查接口
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet,basename='product')

# 3. 将路由器的 URL 加入到 urlpatterns 中
urlpatterns = [
    path('', include(router.urls)),
]