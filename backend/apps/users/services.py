from datetime import date
from django.db import transaction
from .models import CreditLog

class CreditService:
    @staticmethod
    @transaction.atomic
    def update_score(user, amount, reason, action_type):
        """
        统一信用分更新入口
        """
        # 检查是否已经执行过一次性任务 (完善资料或实名)
        if action_type in ['profile', 'verify']:
            if CreditLog.objects.filter(user=user, action_type=action_type).exists():
                return False, "该项加分已获得"

        # 检查发布商品的每日上限 (每天最多2次)
        if action_type == 'post_product':
            today_count = CreditLog.objects.filter(
                user=user, 
                action_type='post_product', 
                create_time__date=date.today()
            ).count()
            if today_count >= 2:
                return False, "今日发布加分已达上限"

        # 计算新分数并锁定上限 100
        new_score = user.credit_score + amount
        if new_score > 100: new_score = 100
        if new_score < 0: new_score = 0
        
        # 保存用户分值
        user.credit_score = new_score
        user.save()
        
        # 记录日志
        CreditLog.objects.create(
            user=user,
            amount=amount,
            reason=reason,
            action_type=action_type
        )
        return True, "更新成功"