from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Report
from .serializers import UserProfileSerializer # 复用之前的
from .serializers import UserProfileSerializer

class AdminUserManagementViewSet(viewsets.ModelViewSet):
    """企业级：全平台用户管理"""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """一键封号/解封 (修改 is_active 字段)"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        status_str = "正常" if user.is_active else "已封禁"
        return Response({'detail': f'用户 {user.username} 状态已变更为 {status_str}'})
   
    # 优化：增加过滤
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        # 根据前端传来的 verify_status 进行过滤
        v_status = self.request.query_params.get('verify_status')
        if v_status:
            queryset = queryset.filter(verify_status=v_status)
        return queryset
    
class AdminReportViewSet(viewsets.ModelViewSet):
    """企业级：违规举报处理"""
    queryset = Report.objects.all().order_by('-create_time')
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        report = self.get_object()
        report.status = 1 # 已处理
        report.save()
        return Response({'detail': '举报处理完成'})