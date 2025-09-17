#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 17:25
# @File    : 5.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QRect
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

    def moveRowUp(self, row):
        if row > 0:
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row - 1)
            self._data[row - 1], self._data[row] = self._data[row], self._data[row - 1]
            self.endMoveRows()

    def moveRowDown(self, row):
        if row < len(self._data) - 1:
            self.beginMoveRows(QModelIndex(), row, row, QModelIndex(), row + 2)
            self._data[row + 1], self._data[row] = self._data[row], self._data[row + 1]
            self.endMoveRows()


# ================= 按钮代理 =================
class ButtonDelegate(QStyledItemDelegate):
    deleteClicked = Signal(int)
    upClicked = Signal(int)
    downClicked = Signal(int)

    def paint(self, painter, option, index):
        """
        绘制表格单元格。
        QStyledItemDelegate 默认只负责绘制单元格内容，我们重写 paint
        方法来在最后一列绘制自定义按钮（删除、上移、下移）。

        参数：
            painter: QPainter 对象，用于绘制内容
            option: QStyleOptionViewItem，单元格绘制选项（位置、大小、状态）
            index: QModelIndex，当前单元格索引
        """

        # 判断是否是最后一列（按钮列）
        if index.column() == index.model().columnCount() - 1:
            # 获取当前单元格的矩形区域
            rect = option.rect

            # 每个按钮宽度为单元格宽度的 1/3
            button_width = rect.width() // 3

            # -------------------- 绘制删除按钮 --------------------
            btn_delete = QStyleOptionButton()
            btn_delete.text = "删除"  # 按钮文字
            btn_delete.rect = QRect(rect.left(), rect.top(), button_width, rect.height())  # 按钮位置
            # 使用当前样式绘制按钮
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_delete, painter)

            # -------------------- 绘制上移按钮 --------------------
            btn_up = QStyleOptionButton()
            btn_up.text = "上移"
            btn_up.rect = QRect(rect.left() + button_width, rect.top(), button_width, rect.height())
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_up, painter)

            # -------------------- 绘制下移按钮 --------------------
            btn_down = QStyleOptionButton()
            btn_down.text = "下移"
            btn_down.rect = QRect(rect.left() + button_width * 2, rect.top(), button_width, rect.height())
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_down, painter)

        else:
            # 非按钮列，使用默认绘制
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        """
        处理用户在表格单元格上的交互事件（点击、鼠标移动等）。
        QStyledItemDelegate 默认只负责绘制单元格，如果想让单元格里的“按钮”可点击，
        就需要重写 editorEvent 来处理鼠标事件。

        参数：
            event: QEvent 对象，表示鼠标或键盘事件
            model: 对应的 QAbstractTableModel
            option: QStyleOptionViewItem，包含单元格的绘制信息，如位置和大小
            index: QModelIndex，表示当前单元格位置
        """

        # 判断是否是最后一列（按钮列）
        if index.column() == index.model().columnCount() - 1:

            # 只处理鼠标释放事件
            if event.type() == event.Type.MouseButtonRelease:

                # 获取当前单元格的矩形区域
                rect = option.rect

                # 每个按钮占据单元格的 1/3
                button_width = rect.width() // 3

                # 鼠标点击位置的 x 坐标
                x = event.pos().x()

                # 判断点击的是哪个按钮
                if x < rect.left() + button_width:
                    # 点击了“删除”按钮
                    self.deleteClicked.emit(index.row())
                elif x < rect.left() + button_width * 2:
                    # 点击了“上移”按钮
                    self.upClicked.emit(index.row())
                else:
                    # 点击了“下移”按钮
                    self.downClicked.emit(index.row())

                # 返回 True 表示事件已处理，不再传递
                return True

        # 对于非按钮列或者非鼠标释放事件，交给父类处理
        return super().editorEvent(event, model, option, index)

"""
+---------------------+
|       QTableView    |
|  显示表格界面       |
+---------------------+
           |
           v
+---------------------+
|  QAbstractTableModel|
|  提供表格数据        |
+---------------------+
           |
           v
+---------------------+
|   ButtonDelegate    |
|  paint()            |  ← 绘制单元格按钮（删除/上移/下移）
|  editorEvent()      |  ← 捕捉鼠标事件，判断点击哪一个按钮
+---------------------+
           |
           v
+---------------------+
|     Signal 发射      |
| deleteClicked(row)  |
| upClicked(row)      |
| downClicked(row)    |
+---------------------+
           |
           v
+---------------------+
|   MainWindow/Controller |
|  接收信号，调用 Model 方法 |
|  修改数据（增删改、移动行）|
+---------------------+
           |
           v
+---------------------+
|     QTableView      |
|  数据更新 → 刷新显示  |
+---------------------+
"""
# ================= 主窗口 =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据驱动表格 + 多操作按钮示例")

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

        delegate.deleteClicked.connect(self.delete_row)
        delegate.upClicked.connect(self.move_up)
        delegate.downClicked.connect(self.move_down)

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

    def move_up(self, row):
        self.model.moveRowUp(row)

    def move_down(self, row):
        self.model.moveRowDown(row)


# ================= 运行 =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 300)
    window.show()
    sys.exit(app.exec())
