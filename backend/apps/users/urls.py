from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,    
)
from .views import RealNameVerifyView, RegisterView, UserProfileView, AddressViewSet, ReportViewSet,MyTokenObtainPairView, ChangePasswordView, ChangeMobileView
from .admin_views import AdminUserManagementViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'addresses', AddressViewSet,basename='addresses')
router.register(r'admin/users', AdminUserManagementViewSet, basename='admin-users')

urlpatterns = [
     path('', include(router.urls)),
    # 注册接口
    path('register/', RegisterView.as_view(), name='register'),
    
    # 登录接口
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    
    # Token 刷新接口
    path('token/refresh/', TokenRefreshView.as_view(), 
         name='token_refresh'),
    # 用户信息
    path('profile/', UserProfileView.as_view(), 
         name='user_profile'),
    # 收货地址
    path('addresses/', AddressViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='address_list_create'),
    # 收货地址详情，更新，删除
    path('addresses/<int:pk>/', AddressViewSet.as_view({'get': 'retrieve', 
                                                        'put': 'update', 
                                                        'delete': 'destroy'
                                                        }), name='address_detail'),
    
    # 实名认证
    path('verify/', RealNameVerifyView.as_view(), name='real_name_verify'),
    # 举报
    path('reports/', ReportViewSet.as_view({'post': 'create'}), name='report_create'),
    # 修改密码
    path('change-password/', ChangePasswordView.as_view()),
    # 修改手机号
    path('change-mobile/', ChangeMobileView.as_view()),
]