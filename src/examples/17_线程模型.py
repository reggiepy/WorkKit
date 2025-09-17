#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/7 16:00
# @File    : 17.py
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# ===================== EventBus =====================
class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.lock = threading.Lock()

    def subscribe(self, key, callback):
        with self.lock:
            self.subscribers[key].append(callback)

    def unsubscribe(self, key, callback):
        with self.lock:
            if callback in self.subscribers[key]:
                self.subscribers[key].remove(callback)

    def publish(self, key, *args, **kwargs):
        with self.lock:
            callbacks = list(self.subscribers[key])
        for cb in callbacks:
            cb(*args, **kwargs)

# ===================== CaptchaManager =====================
class CaptchaManager:
    def __init__(self, account_name):
        self.captcha = None
        self.expire_time = 0
        self.lock = threading.Lock()
        self.account_name = account_name

    def get_captcha(self):
        with self.lock:
            now = time.time()
            if self.captcha is None or now >= self.expire_time:
                self.refresh()
            return self.captcha

    def refresh(self):
        self.captcha = f"captcha-{int(time.time())}"
        self.expire_time = time.time() + 19
        print(f"[{self.account_name}] 刷新验证码: {self.captcha}")

# ===================== BuyerThread =====================
class BuyerThread(threading.Thread):
    def __init__(self, account_id, account_name, event_bus, max_purchase=2):
        super().__init__(daemon=True)
        self.account_id = account_id
        self.account_name = account_name
        self.event_bus = event_bus
        self.captcha_mgr = CaptchaManager(account_name)
        self.max_purchase = max_purchase
        self.owned_products = set()
        self.running = True

    def purchase(self, product):
        captcha = self.captcha_mgr.get_captcha()
        if not captcha:
            print(f"[{self.account_name}] 无有效验证码, 跳过 {product['name']}")
            return
        print(f"[{self.account_name}] 购买 {product['name']} 数量 {product['count']} 使用验证码 {captcha}")
        time.sleep(0.1)  # 模拟购买延迟
        self.owned_products.add(product["id"])
        if len(self.owned_products) >= self.max_purchase:
            self.event_bus.unsubscribe(f"product_{product['id']}_{self.account_id}", self.on_product_available)
            print(f"[{self.account_name}] 达到购买上限, 停止监听商品 {product['name']}")

    def on_product_available(self, product):
        if product["id"] in self.owned_products:
            return
        if product["count"] >= 1:
            self.purchase(product)

    def run(self):
        # 定期刷新验证码
        while self.running:
            self.captcha_mgr.get_captcha()
            time.sleep(5)

# ===================== ProductMonitorThread =====================
class ProductMonitorThread(threading.Thread):
    def __init__(self, event_bus, products, accounts_per_product):
        super().__init__(daemon=True)
        self.event_bus = event_bus
        self.products = products
        self.accounts_per_product = accounts_per_product
        self.executor = ThreadPoolExecutor(max_workers=5)

    def fetch_product_count(self, product):
        time.sleep(0.1)  # 模拟请求延迟
        count = 1  # 模拟库存
        return {"id": product["id"], "name": product["name"], "count": count}

    def run(self):
        while True:
            for product in self.products:
                futures = [self.executor.submit(self.fetch_product_count, product) for _ in range(5)]
                for f in futures:
                    product_data = f.result()
                    for acc_id in self.accounts_per_product.get(product["id"], []):
                        key = f"product_{product['id']}_{acc_id}"
                        self.event_bus.publish(key, product_data)
            time.sleep(1)

# ===================== 测试启动 =====================
def main():
    event_bus = EventBus()

    # 模拟商品
    products = [{"id": 101, "name": "商品A"}, {"id": 102, "name": "商品B"}]

    # 模拟账号
    buyers = [
        {"id": 1, "name": "账号1"},
        {"id": 2, "name": "账号2"},
        {"id": 3, "name": "账号3"}
    ]

    # 商品 -> 账号映射 (谁监听哪个商品)
    accounts_per_product = {
        101: [1, 2],
        102: [2, 3],
    }

    # 启动购买线程
    buyer_threads = []
    for b in buyers:
        t = BuyerThread(b["id"], b["name"], event_bus, max_purchase=2)
        # 订阅自己负责的商品
        for p in products:
            if b["id"] in accounts_per_product.get(p["id"], []):
                key = f"product_{p['id']}_{b['id']}"
                event_bus.subscribe(key, t.on_product_available)
        t.start()
        buyer_threads.append(t)

    # 启动商品监控线程
    monitor = ProductMonitorThread(event_bus, products, accounts_per_product)
    monitor.start()

    # 主线程保持运行
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
