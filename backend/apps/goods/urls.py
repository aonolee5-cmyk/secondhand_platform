from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, BrowsingHistoryViewSet
from .admin_views import AdminProductViewSet, AdminSensitiveWordViewSet, AdminCategoryViewSet 

router = DefaultRouter()


router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet,basename='product')
router.register(r'list', ProductViewSet, basename='product')
router.register(r'admin/sensitive', AdminSensitiveWordViewSet, basename='admin-sensitive')
router.register(r'history', BrowsingHistoryViewSet, basename='history')
router.register(r'admin/categories', AdminCategoryViewSet, basename='admin-category')

urlpatterns = [
    path('', include(router.urls)),
]