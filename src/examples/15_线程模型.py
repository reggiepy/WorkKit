#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/7 11:44
# @File    : 15.py
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, List


class EventBus:
    def __init__(self, max_workers=10):
        self._subscribers = defaultdict(list)
        self._lock = threading.RLock()  # 保护订阅者列表
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        """订阅某个主题"""
        with self._lock:
            self._subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[Any], None]):
        """取消订阅"""
        with self._lock:
            if callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)

    def publish(self, topic: str, data: Any):
        """向某个主题广播消息"""
        with self._lock:
            # 拷贝列表，防止回调修改订阅者导致冲突
            callbacks = list(self._subscribers.get(topic, []))
        for cb in callbacks:
            # 使用线程池异步执行回调，防止阻塞
            self._executor.submit(cb, data)

    def publish_batch(self, topic: str, data_list: List[Any]):
        """批量广播多条消息"""
        with self._lock:
            callbacks = list(self._subscribers.get(topic, []))
        for data in data_list:
            for cb in callbacks:
                self._executor.submit(cb, data)

    def shutdown(self):
        """关闭线程池"""
        self._executor.shutdown(wait=True)


def buyer_task(msg):
    print(f"[BUYER] 收到通知: {msg}")


def monitor_task(msg):
    print(f"[MONITOR] 商品数量: {msg}")


bus = EventBus(max_workers=20)

# 订阅
bus.subscribe("product_available", buyer_task)
bus.subscribe("product_available", monitor_task)

# 发布单条消息
bus.publish("product_available", {"id": 123, "count": 5})

# 批量消息
bus.publish_batch("product_available", [{"id": i, "count": i * 10} for i in range(1, 5)])

# 等待线程处理完成
time.sleep(1)
bus.shutdown()
