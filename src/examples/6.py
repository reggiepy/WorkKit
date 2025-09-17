#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 17:26
# @File    : 6.py
import sys
import time
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QThread
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QPushButton


# ================= 数据模型 =================
class MyTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        if not self._data:
            return 2
        return len(self._data[0])

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return self._data[row][col]

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def addRow(self, row_data):
        """插入一行数据"""
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.append(row_data)
        self.endInsertRows()


# ================= 后台线程 =================
class WorkerThread(QThread):
    finished = Signal(list)  # 处理完成后发射数据

    def __init__(self, task_name):
        super().__init__()
        self.task_name = task_name

    def run(self):
        # 模拟耗时操作
        time.sleep(2)
        # 假设处理结果是一行数据
        result = [self.task_name, "完成"]
        self.finished.emit(result)


# ================= 主窗口 =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("动态添加表格数据示例")

        self.model = MyTableModel([["任务A", "未完成"], ["任务B", "进行中"]])
        self.table = QTableView()
        self.table.setModel(self.model)

        self.add_button = QPushButton("添加任务")
        self.add_button.clicked.connect(self.start_worker)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.add_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_worker(self):
        task_name = f"任务{len(self.model._data) + 1}"
        self.thread = WorkerThread(task_name)
        self.thread.finished.connect(self.add_row_to_model)
        self.thread.start()

    def add_row_to_model(self, row_data):
        self.model.addRow(row_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
