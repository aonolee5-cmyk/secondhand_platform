from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet
from .admin_views import AdminProductViewSet, AdminSensitiveWordViewSet 

router = DefaultRouter()


router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet,basename='product')
router.register(r'list', ProductViewSet)
router.register(r'admin/sensitive', AdminSensitiveWordViewSet, basename='admin-sensitive')

urlpatterns = [
    path('', include(router.urls)),
]