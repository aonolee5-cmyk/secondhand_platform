# backend/apps/users/permissions.py
from rest_framework import permissions

class IsOperationalManager(permissions.BasePermission):
    """
    【等级 1：运营客服/普通管理员】
    只要 is_staff 为 True，就有权访问。
    适用于：商品审核、纠纷仲裁、实名核验。
    """
    def has_permission(self, request, view):
        # 必须登录，且必须是员工（is_staff）或超级管理员
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.is_superuser)
        )

class IsSystemAdmin(permissions.BasePermission):
    """
    【等级 2：系统管理员】
    只有 is_superuser 为 True 才有权访问。
    适用于：敏感词库维护、账号封禁、系统配置。
    """
    def has_permission(self, request, view):
        # 必须登录，且必须是超级管理员
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_superuser
        )

class ActionBasedPermission(permissions.AllowAny):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return IsOperationalManager().has_permission(request, view)
        elif view.action in ['destroy', 'update', 'partial_update']:
            return IsSystemAdmin().has_permission(request, view)
        return False