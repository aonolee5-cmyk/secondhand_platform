import os
import django
import random
import uuid  # 引入UUID保证绝对唯一
from datetime import datetime, timedelta

# 初始化 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from trade.models import Order
from goods.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

def seed_orders():
    print("正在清理旧的模拟数据（可选）...")
    # 如果你想每次都重新生成，可以取消下面这行的注释
    # Order.objects.filter(order_sn__startswith="MOCK").delete()

    print("开始生成企业级模拟交易数据...")
    buyer = User.objects.first()
    products = list(Product.objects.filter(status='onsale')) # 只给在售商品生成订单
    
    if not products:
        print("❌ 错误：数据库中没有‘在售(onsale)’状态的商品，请先去后台修改几个商品状态！")
        return

    count = 0
    # 生成过去 7 天的数据
    for i in range(7):
        # 每天生成不同时间点的订单
        for j in range(random.randint(8, 15)): # 每天多生成几条，图表更好看
            # 这里的 date 要在内层循环生成，保证时间戳不同
            date = datetime.now() - timedelta(days=i, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            try:
                # 🚀 改进后的订单号：MOCK + 时间戳 + 随机字符串 + 循环索引
                unique_id = uuid.uuid4().hex[:6].upper()
                sn = f"MOCK{date.strftime('%Y%m%d')}{unique_id}{count}"
                
                Order.objects.create(
                    order_sn=sn,
                    buyer=buyer,
                    seller=random.choice(products).owner,
                    product=random.choice(products),
                    total_amount=random.randint(100, 2000), # 提高金额让大盘更好看
                    status='paid',
                    create_time=date,
                    pay_time=date
                )
                count += 1
            except Exception as e:
                print(f"跳过一条重复数据: {e}")
                continue
                
    print(f"✅ 成功生成 {count} 条模拟交易数据！快去刷新管理大盘吧。")

if __name__ == "__main__":
    seed_orders()