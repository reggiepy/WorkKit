#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/5 17:31
# @File    : 2.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit
from PySide6.QtCore import Qt, QUrl

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("拖拽文件示例")
        self.setGeometry(200, 200, 500, 400)

        # 用 QTextEdit 来显示拖入的文件路径
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        # 允许拖放
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """当文件拖入窗口时触发"""
        if event.mimeData().hasUrls():  # 检查是否包含文件路径
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """当文件放下时触发"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls]
            self.text_edit.append("拖入的文件：")
            for path in file_paths:
                self.text_edit.append(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
