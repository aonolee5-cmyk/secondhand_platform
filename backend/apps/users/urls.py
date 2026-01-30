from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, # 登录获取 Token
    TokenRefreshView,    # 刷新 Token
)
from .views import RegisterView, UserProfileView, AddressViewSet

urlpatterns = [
    # 注册接口
    path('register/', RegisterView.as_view(), name='register'),
    
    # 登录接口
    path('login/', TokenObtainPairView.as_view(), name='login'),
    
    # Token 刷新接口
    path('token/refresh/', TokenRefreshView.as_view(), 
         name='token_refresh'),
    # 用户信息
    path('profile/', UserProfileView.as_view(), 
         name='user_profile'),
    # 收货地址
    path('addresses/', AddressViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='address_list_create'),
    # 
    path('addresses/<int:pk>/', AddressViewSet.as_view({'get': 'retrieve', 
                                                        'put': 'update', 
                                                        'delete': 'destroy'
                                                        }), name='address_detail'),
]