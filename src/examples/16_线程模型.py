#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/7 11:46
# @File    : 16.py
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Callable, Any, List

# ================= EventBus =================
class EventBus:
    def __init__(self, max_workers=10):
        self._subscribers = defaultdict(list)
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        with self._lock:
            self._subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[Any], None]):
        with self._lock:
            if callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)

    def publish(self, topic: str, data: Any):
        with self._lock:
            callbacks = list(self._subscribers.get(topic, []))
        for cb in callbacks:
            self._executor.submit(cb, data)

    def publish_batch(self, topic: str, data_list: List[Any]):
        with self._lock:
            callbacks = list(self._subscribers.get(topic, []))
        for data in data_list:
            for cb in callbacks:
                self._executor.submit(cb, data)

    def shutdown(self):
        self._executor.shutdown(wait=True)

# ================= Captcha Manager =================
class CaptchaManager:
    """管理验证码状态"""
    def __init__(self):
        self._lock = threading.Lock()
        self.current_captcha = None

    def refresh_captcha(self):
        with self._lock:
            self.current_captcha = f"CAPTCHA-{random.randint(1000,9999)}"
            print(f"[CAPTCHA] Refreshed: {self.current_captcha}")

    def get_captcha(self):
        with self._lock:
            return self.current_captcha

# ================= 商品监控线程 =================
class MonitorThread(threading.Thread):
    def __init__(self, event_bus: EventBus):
        super().__init__(daemon=True)
        self.event_bus = event_bus
        self.running = True

    def run(self):
        while self.running:
            time.sleep(1)  # 模拟商品刷新间隔
            # 模拟商品库存
            product_list = [
                {"id": i, "name": f"商品-{i}", "count": random.randint(0, 10)}
                for i in range(5)
            ]
            for product in product_list:
                if product["count"] > 0:
                    # 满足购买条件时发布消息
                    self.event_bus.publish("product_available", product)

# ================= 购买线程 =================
class BuyerThread(threading.Thread):
    def __init__(self, buyer_id: int, event_bus: EventBus, captcha_mgr: CaptchaManager):
        super().__init__(daemon=True)
        self.buyer_id = buyer_id
        self.event_bus = event_bus
        self.captcha_mgr = captcha_mgr
        self.running = True

    def purchase(self, product):
        captcha = self.captcha_mgr.get_captcha()
        if not captcha:
            print(f"[BUYER-{self.buyer_id}] 无有效验证码，跳过购买 {product['name']}")
            return
        print(f"[BUYER-{self.buyer_id}] 购买 {product['name']} 数量 {product['count']} 使用验证码 {captcha}")

    def on_product_available(self, product):
        if not self.running:
            return
        self.purchase(product)

    def run(self):
        # 订阅商品可购买消息
        self.event_bus.subscribe("product_available", self.on_product_available)
        while self.running:
            time.sleep(1)

# ================= 验证码刷新线程 =================
class CaptchaThread(threading.Thread):
    def __init__(self, captcha_mgr: CaptchaManager):
        super().__init__(daemon=True)
        self.captcha_mgr = captcha_mgr
        self.running = True

    def run(self):
        while self.running:
            time.sleep(5)  # 每 5 秒刷新一次验证码
            self.captcha_mgr.refresh_captcha()

# ==================== 启动示例 ====================
if __name__ == "__main__":
    bus = EventBus(max_workers=20)
    captcha_mgr = CaptchaManager()

    # 启动验证码刷新线程
    captcha_thread = CaptchaThread(captcha_mgr)
    captcha_thread.start()

    # 启动商品监控线程
    monitor_thread = MonitorThread(bus)
    monitor_thread.start()

    # 启动多购买线程
    buyers = [BuyerThread(i, bus, captcha_mgr) for i in range(3)]
    for b in buyers:
        b.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止所有线程...")
        monitor_thread.running = False
        captcha_thread.running = False
        for b in buyers:
            b.running = False
        bus.shutdown()
