from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    自定义用户模型
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="头像")
    
    # 实名认证字段
    real_name = models.CharField(max_length=20, null=True, blank=True, verbose_name="真实姓名")
    id_card = models.CharField(max_length=18, null=True, blank=True, verbose_name="身份证号")
    is_verified = models.BooleanField(default=False, verbose_name="已实名")
    
    # 信用分
    credit_score = models.IntegerField(default=100, verbose_name="信用分")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        db_table = "users_user" # 指定数据库表名

    def __str__(self):
        return self.username