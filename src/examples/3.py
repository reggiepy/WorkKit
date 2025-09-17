#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 17:16
# @File    : 3.py
import sys
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QPushButton, QVBoxLayout, QWidget


class MyTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._headers = ["姓名", "年龄", "城市"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return self._data[index.row()][index.column()]

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = value
            # 通知视图该单元格数据已更新
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        # 可选择 + 可编辑
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            else:
                return str(section + 1)
        return None

    # 添加一个刷新方法，外部更新数据时调用
    def refresh(self):
        self.layoutChanged.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据驱动表格示例")

        # 初始化数据
        self.data = [
            ["张三", 25, "北京"],
            ["李四", 30, "上海"],
            ["王五", 22, "广州"]
        ]

        # 设置表格
        self.model = MyTableModel(self.data)
        self.table = QTableView()
        self.table.setModel(self.model)

        # 按钮：在代码里修改数据
        btn = QPushButton("修改数据（李四 -> 35岁）")
        btn.clicked.connect(self.modify_data)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def modify_data(self):
        # 修改真实数据
        self.data[1][1] = 35
        # 通知表格刷新
        self.model.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(500, 300)
    window.show()
    sys.exit(app.exec())
