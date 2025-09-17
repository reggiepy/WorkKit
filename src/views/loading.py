#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 19:35
# @File    : loading.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget
from PySide6.QtWidgets import QProgressDialog


class LoadingDialog:
    def __init__(self, parent: QWidget = None, text: str = "加载中，请稍候..."):
        self.parent = parent
        self.dialog = QProgressDialog(text, "", 0, 0, parent)
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.setCancelButton(None)
        self.dialog.setMinimumDuration(0)
        self.dialog.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.dialog.setAutoClose(False)  # 不自动关闭
        self.dialog.setAutoReset(False)  # 不自动重置
        self.dialog.close()

    def show(self, text: str = None):
        """显示 loading，可以更新文字"""
        if text:
            self.setText(text)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def close(self):
        """关闭 loading"""
        self.dialog.close()

    def setText(self, text: str):
        """更新提示文字"""
        self.dialog.setLabelText(text)

    def isVisible(self) -> bool:
        return self.dialog.isVisible()
