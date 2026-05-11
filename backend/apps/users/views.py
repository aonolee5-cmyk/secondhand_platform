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
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth.hashers import check_password
from .services import CreditService
from django.utils import timezone
from .models import Report
from .serializers import ReportSerializer


User = get_user_model()

# 注册
@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    """
    用户注册接口
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # 允许未登录用户访问
    serializer_class = RegisterSerializer


# 用户信息    
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    def get_object(self):
        ''' 返回当前登录的用户对象 '''
        return self.request.user

    def perform_update(self, serializer):
        """
        修改用户信息时，如果之前没有完善资料，则加 10 分
        """
        user = self.get_object()
        # 记录更新前的状态：是否已经完善过资料
        # 只要之前 昵称 和 头像 有一个为空，就视为尚未完善
        had_profile = bool(user.nickname and user.avatar)

        # 执行真正的数据库保存
        instance = serializer.save()

        # 逻辑判断：如果之前没完善，现在完善了（都有值了），则加 10 分
        if not had_profile and instance.nickname and instance.avatar:
            success, msg = CreditService.update_score(
                instance, 
                10, 
                "首次完善个人资料（昵称与头像）", 
                "profile"
            )
            if success:
                print(f"DEBUG: 用户 {instance.username} 完善资料加分成功")
    
    def put(self, request,*args, **kwargs):
        ''' 修改用户信息 '''
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        ''' 局部修改用户信息 (头像上传通常走这里) '''
        return self.partial_update(request, *args, **kwargs)
    
# 收货地址视图集
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-id')

    def perform_create(self, serializer):
        '''创建地址'''
        if serializer.validated_data.get('is_default'):
            Address.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='set_default')
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

# 实名认证        
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
            
        # 更新信息
        user.real_name = real_name
        user.id_card = id_card
        user.verify_status = 1  
        user.verify_time = timezone.now()
        user.save()
        
        return Response({'detail': '实名信息已提交，请等待管理员审核'})


 
 # 举报   
class ReportViewSet(viewsets.ModelViewSet):
    ''' 举报视图 '''
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 自动关联举报人
        serializer.save(reporter=self.request.user)
        

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(APIView):
    """
    修改密码接口
    """
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # 校验旧密码
        if not user.check_password(old_password):
            return Response({'detail': '旧密码输入错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 校验新旧密码是否一致
        if old_password == new_password:
            return Response({'detail': '新密码不能与旧密码相同'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 设置新密码并保存
        user.set_password(new_password)
        user.save()
        
        return Response({'detail': '密码修改成功，请重新登录'})
    
class ChangeMobileView(APIView):
    """
    修改手机号接口
    """
    def post(self, request):
        user = request.user
        new_mobile = request.data.get('new_mobile')
        if not new_mobile:
            return Response({'detail': '新手机号不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(mobile=new_mobile).exclude(id=user.id).exists():
            return Response({'detail': '该手机号已被其他账号绑定'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 保存
        user.mobile = new_mobile
        user.save()
        
        return Response({'detail': '手机号修改成功', 'mobile': new_mobile})
    

class ReportViewSet(viewsets.ModelViewSet):
    """
    用户举报接口
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 普通用户只能看到自己发起的举报记录
        if self.request.user.is_staff:
            return Report.objects.all()
        return Report.objects.filter(reporter=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)