import random
import json
from locust import HttpUser, task, between

class SecondHandPlatformUser(HttpUser):
    # 直接压测后端 8000 端口，绕过前端代理，数据更准
    host = "http://127.0.0.1:8000"
    wait_time = between(1, 2)

    def on_start(self):
        """每个模拟用户启动时执行登录，获取真实 Token"""
        res = self.client.post("/api/users/login/", json={
            "username": "jk",
            "password": "262425" 
        })
        if res.status_code == 200:
            self.token = res.json().get('access')
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            print(f"CRITICAL: 登录失败，状态码 {res.status_code}。请检查账号密码！")

    @task(10)
    def view_homepage(self):
        """首页浏览（最稳的接口）"""
        self.client.get("/api/goods/list/?status=onsale", name="/api/goods/list/?onsale")

    @task(5)
    def search_and_filter(self):
        """价格筛选"""
        p_min = random.randint(1, 50)
        p_max = random.randint(500, 2000)
        self.client.get(f"/api/goods/list/?price__gte={p_min}&price__lte={p_max}", name="/api/goods/filter")

    @task(2)
    def post_product_test(self):
        """发布商品测试"""
        # 🚀 专家提示：这里的 category 必须是数据库里存在的 ID
        # 如果 ID 9 报错，请去数据库 goods_category 表看一眼到底 ID 是几
        payload = {
            "title": f"压测宝贝_{random.randint(100,999)}",
            "desc": "这是一段模拟长描述" * 10,
            "price": "88.00",
            "category": 9, # 👈 确认这个 ID 在数据库里有！
            "images": ["/media/products/test.jpg"],
            "attributes": {"成色": "全新"}
        }
        self.client.post("/api/goods/list/", json=payload, name="/api/goods/post")

    @task(1)
    def place_order_test(self):
        """下单测试（高并发行级锁测试）"""
        # 🚀 重点修复：将 product_id 改为 product，以对齐后端 Serializer 字段
        # 🚀 重点修复：ID 范围设为 9-15（基于你提供的信息）
        target_product_id = random.randint(9, 15)
        
        order_payload = {
            "product": target_product_id, # 👈 必须叫 product，不能叫 product_id
            "address": {
                "receiver": "压测员",
                "mobile": "13800001111",
                "region": "测试省市",
                "detail": "测试街道"
            }
        }
        self.client.post("/api/trade/orders/", json=order_payload, name="/api/trade/orders/post")