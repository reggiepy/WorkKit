#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/2 13:45
# @File    : 1.py
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout
import sys
import time

# 后台线程
class Worker(QThread):
    update_signal = Signal(int, str)  # 传递行号和状态

    def run(self):
        for i in range(5):
            time.sleep(1)  # 模拟耗时操作
            self.update_signal.emit(i, "完成")  # 发射信号

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget(5, 2)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        # 启动后台线程
        self.worker = Worker()
        self.worker.update_signal.connect(self.update_table)
        self.worker.start()

        # QTimer 示例（倒计时）
        self.timer_count = 10
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_tick)
        self.timer.start(1000)  # 每秒触发一次

    def update_table(self, row, status):
        self.table.setItem(row, 1, QTableWidgetItem(status))

    def timer_tick(self):
        self.timer_count -= 1
        self.setWindowTitle(f"倒计时: {self.timer_count}s")
        if self.timer_count <= 0:
            self.timer.stop()

app = QApplication(sys.argv)
w = MyWindow()
w.show()
sys.exit(app.exec_())
