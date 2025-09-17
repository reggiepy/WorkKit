#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 17:33
# @File    : 7.py
import sys
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import (
    QApplication, QTableView, QStyledItemDelegate, QStyle, QStyleOptionProgressBar
)


# ================= 数据模型 =================
class MyTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data  # 每行最后一列是进度（0~100）

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0])

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[row][col]

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            row, col = index.row(), index.column()
            self._data[row][col] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable


# ================= 进度条代理 =================
class ProgressBarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 2:  # 假设第3列是进度列
            progress = index.data()
            progressBarOption = QStyleOptionProgressBar()
            progressBarOption.rect = option.rect
            progressBarOption.minimum = 0
            progressBarOption.maximum = 100
            progressBarOption.progress = int(progress)
            progressBarOption.text = f"{progress}%"
            progressBarOption.textVisible = True
            QApplication.style().drawControl(QStyle.ControlElement.CE_ProgressBar, progressBarOption, painter)
        else:
            super().paint(painter, option, index)


# ================= 主窗口 =================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    data = [
        ["任务A", "未完成", 20],
        ["任务B", "进行中", 50],
        ["任务C", "已完成", 100]
    ]

    model = MyTableModel(data)
    table = QTableView()
    table.setModel(model)

    # 设置进度条代理
    delegate = ProgressBarDelegate(table)
    table.setItemDelegateForColumn(2, delegate)

    table.resize(500, 200)
    table.show()
    sys.exit(app.exec())
