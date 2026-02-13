from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ReviewViewSet, CartViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]