from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, ReportSerializer
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Address, Report
from .serializers import UserProfileSerializer, AddressSerializer
from rest_framework.decorators import action
from rest_framework import status
# from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

User = get_user_model()
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    """
    用户注册接口
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # 允许未登录用户访问
    serializer_class = RegisterSerializer
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    def get_object(self):
        ''' 返回当前登录的用户对象 '''
        return self.request.user

    def put(self, request,*args, **kwargs):
        ''' 修改用户信息 '''
        return self.update(request, *args, **kwargs)

# 收货地址视图集
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-id')

    def perform_create(self, serializer):
        ''' 创建地址时关联当前用户 '''
        if serializer.validated_data.get('is_default'):
            # 如果新创建的地址设为默认地址，则将其他地址设为非默认
            Address.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        ''' 设置默认地址 '''
        address = self.get_object()
        # 将当前用户的所有地址设为非默认
        Address.objects.filter(user=request.user).update(is_default=False)
        # 将选中的地址设为默认
        address.is_default = True
        address.save()
        return Response({'status': '设置成功'})
    def perform_update(self, serializer):
        ''' 修改地址时关联当前用户 '''
        if serializer.validated_data.get('is_default'):
            # 如果新创建的地址设为默认地址，则将其他地址设为非默认
            Address.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(user=self.request.user)
        
class RealNameVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        if user.verify_status == 2:
            return Response({'detail': '您已通过实名认证，无需重复提交'}, status=400)
            
        # 获取上传的数据
        real_name = request.data.get('real_name')
        id_card = request.data.get('id_card')
        
        if not real_name or not id_card:
            return Response({'detail': '请完整填写姓名和身份证号'}, status=400)
            
        # 更新用户信息
        user.real_name = real_name
        user.id_card = id_card
        user.verify_status = 1  # 设为审核中
        user.save()
        
        return Response({'detail': '实名信息已提交，请等待管理员审核'})
    
class ReportViewSet(viewsets.ModelViewSet):
    ''' 举报视图 '''
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 自动关联举报人
        serializer.save(reporter=self.request.user)