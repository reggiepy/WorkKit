#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 17:20
# @File    : 4.py
import sys
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout,
    QWidget, QStyledItemDelegate, QStyle, QStyleOptionButton, QMessageBox
)


# ================= 数据模型 =================
class MyTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data  # 数据源是个二维列表

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) + 1  # 最后一列放按钮

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()

        # 按钮列不显示文本
        if col == len(self._data[0]):
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self._data[row][col]

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            row, col = index.row(), index.column()
            if col < len(self._data[0]):
                self._data[row][col] = value
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        # 最后一列是按钮，不可编辑
        if index.column() == len(self._data[0]):
            return Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._data[0]):
                    return f"列 {section}"
                else:
                    return "操作"
            else:
                return f"行 {section}"
        return None

    def removeRow(self, row, parent=QModelIndex()):
        if 0 <= row < len(self._data):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._data.pop(row)
            self.endRemoveRows()
            return True
        return False


# ================= 按钮代理 =================
class ButtonDelegate(QStyledItemDelegate):
    clicked = Signal(int)  # 传递行号

    def paint(self, painter, option, index):
        if index.column() == index.model().columnCount() - 1:
            button = QStyleOptionButton()
            button.text = "删除"
            button.rect = option.rect
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, button, painter)
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if index.column() == index.model().columnCount() - 1:
            if event.type() == event.Type.MouseButtonRelease:
                self.clicked.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)


# ================= 主窗口 =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据驱动表格 + 按钮示例")

        # 初始化数据
        data = [
            ["任务A", "未完成"],
            ["任务B", "进行中"],
            ["任务C", "已完成"]
        ]

        self.model = MyTableModel(data)
        self.table = QTableView()
        self.table.setModel(self.model)

        # 设置按钮代理到最后一列
        delegate = ButtonDelegate(self.table)
        self.table.setItemDelegateForColumn(self.model.columnCount() - 1, delegate)
        delegate.clicked.connect(self.delete_row)

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def delete_row(self, row):
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除第 {row+1} 行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.removeRow(row)


# ================= 运行 =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 300)
    window.show()
    sys.exit(app.exec())
