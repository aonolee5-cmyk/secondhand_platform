from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    """
    用户注册接口
    POST /api/users/register/
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # 允许未登录用户访问
    serializer_class = RegisterSerializer