#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/10 10:20
# @File    : single_page_pdf.py
from pathlib import Path
from typing import Union

import fitz
from PySide6.QtCore import (
    Signal,
    Qt,
    QAbstractTableModel,
    QModelIndex, QObject, QEvent,
)
from PySide6.QtGui import QDropEvent, QDragEnterEvent, QDragMoveEvent, QDragLeaveEvent
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
)


class InvoicePdfTableModel(QAbstractTableModel):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)
        self.files = []  # 示例：{"filename": 1, "filepath": "unknown", "pagesize":"", "file_range": "", "status", ""}

    # 返回表格行数，即任务数量
    def rowCount(self, parent=QModelIndex()):
        return len(self.files)

    # 返回表格列数
    def columnCount(self, parent=QModelIndex()):
        return 6  # 包含 文件名、页数、范围、文件状态、操作

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        account = self.files[index.row()]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return account.get("filename")
            elif col == 1:
                return account.get("filepath")
            elif col == 2:
                return account.get("pagesize")
            elif col == 3:
                return account.get("file_range")
            elif col == 4:
                return account.get("status")
        elif role == Qt.ItemDataRole.BackgroundRole:
            pass
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """更新本地缓存 + 提交数据库"""
        if index.isValid():
            if role == Qt.ItemDataRole.EditRole:
                account = self.files[index.row()]
                row = index.row()
                col = index.column()
                # if col == 1:  # 用户名列
                #     account["username"] = value
                # elif col == 2:  # 登录状态列
                #     account["login_status"] = value
                # self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if index.column() in [
            0, 1, 2, 3, 4, 5
        ]:
            return Qt.ItemFlag.ItemIsEnabled  # 按钮列不可编辑
        return (
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsEditable
        )

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            # 水平表头 文件名、页数、范围、文件状态、操作
            return ["文件名", "文件路径", "页数", "范围", "文件状态", "操作"][section]
        # 垂直表头显示行号
        return str(section + 1)

    # ---- 槽函数，用于接收外部信号更新模型 ----
    def on_delete_row(self, row: int):
        """删除指定行"""
        if 0 <= row < len(self.files):
            filepath = self.files[row]["filepath"]
            self.on_file_deleted(filepath)

    def on_move_up(self, row: int):
        """上移行"""
        if row > 0:
            self.files[row - 1], self.files[row] = self.files[row], self.files[row - 1]
            self._refresh_rows(row - 1, row)

    def on_move_down(self, row: int):
        """下移行"""
        if row < len(self.files) - 1:
            self.files[row + 1], self.files[row] = self.files[row], self.files[row + 1]
            self._refresh_rows(row, row + 1)

    def _refresh_rows(self, start: int, end: int):
        """刷新指定范围行"""
        top_left = self.index(start, 0)
        bottom_right = self.index(end, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    # 当任务列表加载完成时，刷新整个表格
    def on_files_loaded(self, files):
        self.beginResetModel()  # 通知视图开始重置
        self.files = files
        self.endResetModel()  # 通知视图结束重置

    # 当插入新任务时，追加到表格末尾
    def on_file_inserted(self, account):
        row = len(self.files)  # 新行索引
        self.beginInsertRows(QModelIndex(), row, row)  # 通知视图插入行
        self.files.append(account)
        self.endInsertRows()  # 通知视图插入完成

    # 当删除任务时，根据 task_id 找到行并删除
    def on_file_deleted(self, filepath):
        row = next(
            (i for i, t in enumerate(self.files) if t["filepath"] == filepath), -1
        )
        if row >= 0:
            self.beginRemoveRows(QModelIndex(), row, row)  # 通知视图开始删除行
            del self.files[row]
            self.endRemoveRows()  # 通知视图删除完成


# ==================== 按钮代理 ====================
class InvoicePdfButtonDelegate(QStyledItemDelegate):
    deleteClicked = Signal(int)
    upClicked = Signal(int)
    downClicked = Signal(int)

    def paint(self, painter, option, index):
        if index.column() == 5:
            rect = option.rect
            w = rect.width() // 3
            btn_delete = QStyleOptionButton()
            btn_delete.text = "删除"
            btn_delete.rect = rect.adjusted(0, 0, -2 * w, 0)
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_delete, painter)

            btn_up = QStyleOptionButton()
            btn_up.text = "上移"
            btn_up.rect = rect.adjusted(w, 0, -w, 0)
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_up, painter)

            btn_down = QStyleOptionButton()
            btn_down.text = "下移"
            btn_down.rect = rect.adjusted(2 * w, 0, 0, 0)
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_down, painter)
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if index.column() == 5 and event.type() == event.Type.MouseButtonRelease:
            rect = option.rect
            w = rect.width() // 3
            x = event.position().x() - rect.left()
            if x < w:
                self.deleteClicked.emit(index.row())
            elif x < 2 * w:
                self.upClicked.emit(index.row())
            else:
                self.downClicked.emit(index.row())
            return True
        return super().editorEvent(event, model, option, index)


class InvoicePdfDropFilter(QObject):
    def __init__(self, table_model: InvoicePdfTableModel, parent=None):
        super().__init__(parent)
        self.table_model = table_model

    def eventFilter(self, obj, event: Union[QEvent, QDropEvent, QDragEnterEvent]):
        if event.type() == QEvent.Type.DragEnter:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True
        elif event.type() == QEvent.Type.Drop:
            for url in event.mimeData().urls():
                file_path = Path(url.toLocalFile())
                if file_path.suffix != ".pdf":
                    continue
                doc = fitz.open(file_path.as_posix())
                page_start = 1
                page_end = doc.page_count
                file_info = {
                    "filename": file_path.name,
                    "filepath": file_path.as_posix(),
                    "pagesize": doc.page_count,
                    "file_range": f"{page_start}-{page_end}",
                    "status": "加载成功"
                }
                doc.close()
                self.table_model.on_file_inserted(file_info)
            return True
        return super().eventFilter(obj, event)
