#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 17:36
# @File    : 8.py
import sys
import time
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QThread, Signal
from PySide6.QtWidgets import QApplication, QTableView, QStyledItemDelegate, QStyle, QStyleOptionProgressBar


# ================= 数据模型 =================
class MyTableModel(QAbstractTableModel):
    """自定义表格数据模型"""
    def __init__(self, data):
        super().__init__()
        self._data = data  # 数据源是二维列表 [[任务名, 状态, 进度], ...]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0])

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """返回单元格数据"""
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[row][col]

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """修改单元格数据，同时发出 dataChanged 信号刷新视图"""
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            row, col = index.row(), index.column()
            self._data[row][col] = value
            # 通知视图刷新
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False

    def flags(self, index):
        """设置单元格可选、可编辑状态"""
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled


# ================= 进度条代理 =================
class ProgressBarDelegate(QStyledItemDelegate):
    """自定义代理，在指定列绘制进度条"""
    def paint(self, painter, option, index):
        if index.column() == 2:  # 第3列显示进度条
            progress = index.data()
            progressBarOption = QStyleOptionProgressBar()
            progressBarOption.rect = option.rect
            progressBarOption.minimum = 0
            progressBarOption.maximum = 100
            progressBarOption.progress = int(progress)
            progressBarOption.text = f"{progress}%"
            progressBarOption.textVisible = True
            # 绘制进度条
            QApplication.style().drawControl(QStyle.ControlElement.CE_ProgressBar, progressBarOption, painter)
        else:
            # 其他列使用默认绘制
            super().paint(painter, option, index)


# ================= 后台线程 =================
class WorkerThread(QThread):
    """后台线程，用于模拟任务进度更新"""
    progressUpdated = Signal(int, int)  # 发射信号：row, progress

    def run(self):
        """线程运行逻辑"""
        for i in range(101):
            time.sleep(0.1)  # 模拟耗时任务
            self.progressUpdated.emit(0, i)  # 更新第0行进度


# ================= 主程序 =================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 初始化表格数据
    data = [
        ["任务A", "未完成", 0],
        ["任务B", "进行中", 0],
        ["任务C", "已完成", 0]
    ]

    model = MyTableModel(data)
    table = QTableView()
    table.setModel(model)

    # 设置进度条代理
    delegate = ProgressBarDelegate(table)
    table.setItemDelegateForColumn(2, delegate)

    table.resize(500, 200)
    table.show()

    # 启动后台线程更新第0行进度
    worker = WorkerThread()
    worker.progressUpdated.connect(
        lambda row, value: model.setData(model.index(row, 2), value)
    )
    worker.start()

    sys.exit(app.exec())
