from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    用户模型
    """
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="头像")
    nickname = models.CharField(max_length=30, null=True, blank=True, verbose_name="昵称")
    bio = models.TextField(null=True, blank=True, verbose_name="个人简介")
    
    # 实名认证字段
    real_name = models.CharField(max_length=20, null=True, blank=True, verbose_name="真实姓名")
    id_card = models.CharField(max_length=18, null=True, blank=True, verbose_name="身份证号")
    is_verified = models.BooleanField(default=False, verbose_name="已实名")
    
    VERIFY_STATUS_CHOICES =(
        (0,'未提交'),
        (1,'审核中'),
        (2,'已认证'),
        (3,'认证失败'),
    )
    
    verify_status = models.SmallIntegerField(choices=VERIFY_STATUS_CHOICES, default=0, verbose_name="实名认证状态")
    
    # 信用分
    credit_score = models.IntegerField(default=100, verbose_name="信用分")
    @property
    def credit_level(self):
        ''' 根据信用分计算信用等级'''
        if self.credit_score >= 90:
            return {'text': '信用极好', 'color': '#67C23A', 'type': 'success'}
        elif self.credit_score >= 70:
            return {'text': '信用良好', 'color': '#409EFF', 'type': 'primary'}
        elif self.credit_score >= 60:
            return {'text': '信用中等', 'color': '#E6A23C', 'type': 'warning'}
        else:
            return {'text': '信用极差', 'color': '#F56C6C', 'type': 'danger'}
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        db_table = "users_user" # 指定数据库表名

class Address(models.Model):
    ''' 收货地址模型 '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    receiver = models.CharField(max_length=20, verbose_name="收货人")
    mobile = models.CharField(max_length=11, verbose_name="联系电话")
    region = models.CharField(max_length=100, verbose_name="省市区")
    detail = models.CharField(max_length=255, verbose_name="详细地址")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")

    class Meta:
        verbose_name = "收货地址"
        db_table = "users_address"
    def __str__(self):
        return self.username
    
class Report(models.Model):
    """违规举报模型"""
    REPORT_REASONS = (
        ('fake', '虚假信息'),
        ('advertising', '广告骚扰'),
        ('insult', '言语辱骂'),
        ('scam', '诈骗行为'),
        ('other', '其他原因'),
    )

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made", verbose_name="举报人")
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received", verbose_name="被举报人")
    product = models.ForeignKey('goods.Product', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联商品")
    
    reason = models.CharField(max_length=20, choices=REPORT_REASONS, verbose_name="举报理由")
    content = models.TextField(verbose_name="详情描述")
    status = models.IntegerField(default=0, choices=((0, '待处理'), (1, '已处理')), verbose_name="处理状态")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "违规举报"
        verbose_name_plural = verbose_name