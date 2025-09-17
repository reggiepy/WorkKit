#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/8 11:48
# @File    : 19_表格刷新状态.py
import sys
import time

from PySide6.QtCore import Qt, QThread, Signal, QObject, QAbstractTableModel, QModelIndex, Slot
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


# ---------------- AccountRepository ----------------
class AccountRepository(QObject):
    """后台账号仓库，管理测试登录"""

    # 对外信号
    account_login = Signal(str, str)  # username, status

    # 内部信号
    _test_account_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建后台线程
        self._thread = QThread(self)
        self.moveToThread(self._thread)
        self._thread.start()

        # 内部信号绑定槽函数
        self._test_account_signal.connect(self._slot_test_account)

    # 外部调用接口，发射内部信号
    def test_account_login(self, username):
        self._test_account_signal.emit(username)

    # 后台线程执行耗时操作
    @Slot(str)
    def _slot_test_account(self, username):
        # 发出 testing 状态
        self.account_login.emit(username, "testing")
        time.sleep(2)  # 模拟网络请求
        # 登录成功
        self.account_login.emit(username, "success")

    def shutdown(self):
        """安全关闭线程"""
        self._thread.quit()  # 请求线程退出事件循环
        self._thread.wait()  # 等待线程结束
        print("AccountRepository 已安全关闭")


# ---------------- 表格模型 ----------------
class ScanAccountTableModel(QAbstractTableModel):
    def __init__(self, accounts=None):
        super().__init__()
        self.accounts = accounts or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.accounts)

    def columnCount(self, parent=QModelIndex()):
        return 2  # 用户名、状态

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


# ---------------- 主窗口 ----------------
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

        # 创建后台账号仓库
        self.account_repo = AccountRepository()
        self.account_repo.account_login.connect(self.model.update_status)

    def test_login(self):
        username = "user1"
        self.account_repo.test_account_login(username)

    def closeEvent(self, event):
        # 安全关闭后台仓库线程
        self.account_repo.shutdown()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
