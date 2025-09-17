#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/3 16:16
# @File    : thread.py
import threading
import time
from typing import Optional


class StoppableThread(threading.Thread):
    """
    通用线程类，支持启动、停止、暂停、恢复
    """

    def __init__(
            self,
            target=None,
            args=(),
            kwargs=None,
            name=None,
            stop_event: threading.Event = None,
            paused: bool = False,
            pause_cond: Optional[threading.Condition] = None,
    ):
        super().__init__(name=name)
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}
        self._stop_event = stop_event if stop_event else threading.Event()
        self._pause_cond = (
            pause_cond if pause_cond else threading.Condition(threading.Lock())
        )
        self._paused = paused

    def run(self):
        while not self._stop_event.is_set():
            # 暂停处理
            with self._pause_cond:
                while self._paused:
                    self._pause_cond.wait()

            # 执行目标函数
            if self._target:
                self._target(*self._args, **self._kwargs)
            else:
                time.sleep(0.1)  # 默认空循环防止 CPU 占用过高

    def stop(self):
        """停止线程"""
        self._stop_event.set()
        self.resume()  # 如果线程被暂停，先唤醒再停止

    def pause(self):
        """暂停线程"""
        with self._pause_cond:
            self._paused = True

    def resume(self):
        """恢复线程"""
        with self._pause_cond:
            self._paused = False
            self._pause_cond.notify_all()
