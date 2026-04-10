from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ReviewViewSet, CartViewSet, FavoriteViewSet
from .admin_views import AdminOrderViewSet, AdminDashboardStatsView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'admin/orders', AdminOrderViewSet, basename='admin-orders')
router.register(r'favorites', FavoriteViewSet, basename='favorites') 

urlpatterns = [
    path('admin/dashboard/', AdminDashboardStatsView.as_view(), name='admin-dashboard'),
    path('', include(router.urls)),    
]