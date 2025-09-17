#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 19:39
# @File    : 12.py
from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow
from PySide6.QtCore import Signal, QObject
from threading import Thread
import time

from views.loading import LoadingDialog

class Worker(QObject):
    update_text = Signal(str)
    finished = Signal()

    def run(self):
        for i in range(5):
            time.sleep(1)
            self.update_text.emit(f"任务进行中... {i+1}/5")
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading 封装示例")

        btn = QPushButton("开始任务", self)
        btn.clicked.connect(self.start_task)
        self.setCentralWidget(btn)

        self.loading = LoadingDialog(self, "初始化...")

    def start_task(self):
        self.loading.show("任务处理中...")

        self.worker = Worker()
        self.worker.update_text.connect(self.loading.setText)
        self.worker.finished.connect(self.loading.close)

        Thread(target=self.worker.run, daemon=True).start()


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.resize(300, 200)
    win.show()
    app.exec()

