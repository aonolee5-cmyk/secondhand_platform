from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, # 登录获取 Token
    TokenRefreshView,    # 刷新 Token
)
from .views import RegisterView

urlpatterns = [
    # 注册
    path('register/', RegisterView.as_view(), name='register'),
    
    # 登录 (直接使用 simplejwt 提供的标准接口)
    # 只需要传 username 和 password，它会返回 access 和 refresh token
    path('login/', TokenObtainPairView.as_view(), name='login'),
    
    # 刷新 token (access token 过期后用 refresh token 换新的)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]