import os
import django
import random
from datetime import datetime, timedelta, date
# 🚀 1. 引入 Django 的时区工具
from django.utils import timezone

# 初始化 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from trade.models import Order
from goods.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

def seed_enterprise_data():
    print("🚀 开始灌入跨季度运营模拟数据...")
    
    start_date = date(2026, 1, 28)
    end_date = date.today()
    
    buyer = User.objects.filter(is_staff=False).first()
    products = list(Product.objects.all())
    
    if not products:
        print("❌ 错误：请先发布几个商品！")
        return

    current_date = start_date
    total_count = 0

    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        base_orders = random.randint(8, 15) if is_weekend else random.randint(3, 7)
        
        for _ in range(base_orders):
            # 生成原始时间
            naive_time = datetime.combine(current_date, datetime.min.time()) + timedelta(
                                        hours=random.randint(8, 23), 
                                        minutes=random.randint(0, 59))
            
            # 🚀 2. 核心修复：将“朴素时间”转换为“带时区的觉醒时间”
            random_time = timezone.make_aware(naive_time)
            
            Order.objects.create(
                order_sn=f"MOCK{random_time.strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}",
                buyer=buyer,
                seller=random.choice(products).owner,
                product=random.choice(products),
                total_amount=random.randint(100, 1500),
                status='paid',
                create_time=random_time,
                pay_time=random_time
            )
            total_count += 1
        
        print(f"✅ 已完成 {current_date} 的数据模拟")
        current_date += timedelta(days=1)

    print(f"✨ 成功！共生成 {total_count} 笔订单。警告已消除。")

if __name__ == "__main__":
    seed_enterprise_data()