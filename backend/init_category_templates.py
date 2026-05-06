import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from goods.models import Category

templates = {
    '数码产品': ['品牌', '型号', '内存容量', '电池效率', '保修情况'],
    '图书影音': ['作者', '出版社', '版本/印次', 'ISBN编号', '成色'],
    '农用物品': ['机械种类', '动力功率', '使用时长', '主要用途'],
    '文玩': ['材质', '年代/生产日期', '鉴定证书', '尺寸规格'],
    '母婴': ['品牌', '材质安全', '适用年龄', '消毒情况'],
    '潮玩': ['系列', '款式', '状态', '是否拆袋'],
    '户外': ['品牌', '重量/规格', '防水性能', '面料科技'],
    '家电': ['品牌', '能效等级', '外形尺寸', '功能完好度'],
    '家居日用': ['材质', '尺寸', '使用状态', '风格'],
    '美妆': ['品牌', '保质期/到期日', '是否拆封', '购买渠道'],
    '穿搭': ['品牌', '尺码', '面料成分', '适用季节'],
    '工艺礼品': ['工艺材质', '包装情况', '寓意主题', '产地']
}

def migrate_templates():
    for cat_name, fields in templates.items():
        cat, created = Category.objects.get_or_create(name=cat_name)
        cat.attribute_fields = fields
        cat.save()
        print(f"✅ 已同步分类：{cat_name} -> {fields}")

if __name__ == "__main__":
    migrate_templates()