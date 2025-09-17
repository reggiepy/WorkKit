#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/8 11:19
# @File    : 18_表格刷新状态.py
import sys
import time
from PySide6.QtCore import Qt, QThread, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import QApplication, QTableView, QPushButton, QVBoxLayout, QWidget

# 模拟状态文字
def get_status_text(status):
    texts = {
        "unknown": "未知",
        "testing": "测试中",
        "success": "成功",
        "failed": "失败"
    }
    return texts.get(status, status)


# 后台线程：模拟登录过程
class LoginThread(QThread):
    login_result = Signal(str, str)  # username, status

    def __init__(self, username):
        super().__init__()
        self.username = username

    def run(self):
        # 发出 testing 状态
        self.login_result.emit(self.username, "testing")
        time.sleep(2)  # 模拟网络请求
        # 登录成功
        self.login_result.emit(self.username, "success")


# 表格模型
class ScanAccountTableModel(QAbstractTableModel):
    def __init__(self, accounts=None):
        super().__init__()
        self.accounts = accounts or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.accounts)

    def columnCount(self, parent=QModelIndex()):
        return 3  # 用户名、状态、操作

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        account = self.accounts[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return account.get("username")
            elif col == 1:
                return get_status_text(account.get("login_status"))

        if role == Qt.BackgroundRole and col == 1:
            status = account.get("login_status")
            colors = {
                "unknown": Qt.yellow,
                "testing": Qt.cyan,
                "success": Qt.green,
                "failed": Qt.red
            }
            color = colors.get(status, Qt.white)
            return QBrush(color)

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    # 更新状态
    def update_status(self, username, status):
        row = next((i for i, t in enumerate(self.accounts) if t["username"] == username), -1)
        if row >= 0:
            self.accounts[row]["login_status"] = status
            idx = self.index(row, 1)
            self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.BackgroundRole])


# 主窗口
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("账户登录测试")

        accounts = [
            {"username": "user1", "login_status": "unknown"},
            {"username": "user2", "login_status": "unknown"},
            {"username": "user3", "login_status": "unknown"},
        ]

        self.model = ScanAccountTableModel(accounts)
        self.view = QTableView()
        self.view.setModel(self.model)

        self.button = QPushButton("测试登录 user1")
        self.button.clicked.connect(self.test_login)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 保存线程引用，防止被回收
        self.threads = []

    def test_login(self):
        username = "user1"
        thread = LoginThread(username)
        thread.login_result.connect(self.model.update_status)
        thread.finished.connect(lambda: self.threads.remove(thread))  # 线程结束后移除引用
        self.threads.append(thread)
        thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
