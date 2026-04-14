import os
import django
import random
from decimal import Decimal

# 1. 初始化 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from goods.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

# 🚀 辅助函数：根据你的真实分类获取匹配的图片
def get_real_image_url(cat_name):
    keyword_map = {
        "数码产品": "iphone,laptop,camera",
        "图书影音": "book,vinyl,cd",
        "农用物品": "tractor,tools,farm",
        "文玩": "jade,wood,antique",
        "母婴": "baby,toy",
        "潮玩": "lego,figure,popmart",
        "户外": "tent,hiking,bicycle",
        "家电": "fridge,tv,washing-machine",
        "家居日用": "sofa,table,lamp",
        "美妆": "lipstick,makeup",
        "穿搭": "clothes,sneakers,watch",
        "工艺礼品": "gift,craft"
    }
    kw = "object"
    for k, v in keyword_map.items():
        if k in cat_name:
            kw = v
            break
    return f"https://loremflickr.com/400/400/{kw}?lock={random.randint(1, 9999)}"

def seed_products(count=50):
    print(f"🚀 开始根据真实分类批量上架 {count} 件商品...")
    
    users = list(User.objects.filter(is_superuser=False))
    categories = list(Category.objects.all())

    if not users or not categories:
        print("❌ 错误：请确保数据库中有普通用户和分类！")
        return

    # 匹配你截图里的真实分类名
    titles_pool = {
        "数码产品": ["iPhone 15", "华为平板", "机械键盘", "索尼耳机"],
        "图书影音": ["考研资料", "三体全集", "周杰伦专辑", "摄影教程"],
        "潮玩": ["泡泡玛特盲盒", "乐高机械组", "高达模型"],
        "户外": ["迪卡侬帐篷", "登山包", "山地自行车"],
        "穿搭": ["耐克运动鞋", "潮牌卫衣", "复古牛仔裤"],
        "家居日用": ["人体工学椅", "香薰机", "全身镜"]
    }

    def generate_attrs(cat_name):
        if "数码" in cat_name:
            return {"成色": "95新", "电池": "98%", "保修": "在保"}
        elif "图书" in cat_name:
            return {"版本": "原版", "笔记": "无笔记"}
        elif "穿搭" in cat_name:
            return {"尺码": "L码", "颜色": "黑色"}
        return {"入手时间": "2023年", "状态": "完好"}

    created_count = 0
    for i in range(count):
        category = random.choice(categories)
        owner = random.choice(users)
        
        # 寻找标题池，找不到就用通用标题
        pool = titles_pool.get(category.name, ["闲置好物", "毕业清仓", "超值二手"])
        title = random.choice(pool) + f"_{random.randint(10, 99)}"
        
        img_url = get_real_image_url(category.name)

        try:
            Product.objects.create(
                owner=owner,
                category=category,
                title=title,
                desc=f"出个自用的{title}，成色如图，功能全部正常。校内面交或者邮寄都行，非诚勿扰。",
                price=Decimal(str(random.randint(20, 2000))),
                attributes=generate_attrs(category.name),
                images=[img_url],
                status='onsale',
                # 🚀 如果你没加字段，就把下面这行删掉
                browse_count=random.randint(5, 500) 
            )
            created_count += 1
            if created_count % 5 == 0:
                print(f"已成功上架 {created_count} 件...")
        except Exception as e:
            print(f"第 {i} 件失败: {e}")

    print(f"✅ 成功完成！共上架 {created_count} 件商品。")

if __name__ == "__main__":
    seed_products(40)