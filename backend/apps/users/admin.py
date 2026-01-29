from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 注册自定义用户模型，这样 admin 后台就能管理用户了
admin.site.register(User, UserAdmin)