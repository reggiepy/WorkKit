#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 19:33
# @File    : 11.py
import sys
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QProgressBar, QPushButton


class LoadingDialog(QDialog):
    def __init__(self, text="加载中，请稍候...", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setFixedSize(300, 100)

        self.layout = QVBoxLayout(self)
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 0,0 表示无限加载

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress)

    def setText(self, text):
        """更新提示文字"""
        self.label.setText(text)


# 测试非阻塞更新提示文字
class Worker(QObject):
    updateText = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        import time
        for i in range(5):
            time.sleep(1)
            self.updateText.emit(f"加载中... {i+1}/5")
        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dlg = LoadingDialog("初始化...")
    dlg.show()

    # 模拟后台任务
    worker = Worker()
    worker.updateText.connect(dlg.setText)
    worker.finished.connect(dlg.close)

    from threading import Thread
    t = Thread(target=worker.run)
    t.start()

    sys.exit(app.exec())
