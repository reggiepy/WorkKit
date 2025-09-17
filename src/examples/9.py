#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 17:48
# @File    : 9.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import uuid
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QTableView, QStyledItemDelegate, QStyle, QStyleOptionProgressBar,
    QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox
)


# ================= 数据模型 =================
class Task:
    """每行任务数据对象"""
    def __init__(self, name, status="未完成"):
        self.task_id = uuid.uuid4().hex  # 唯一标识
        self.name = name
        self.status = status
        self.progress = 0


class MyTableModel(QAbstractTableModel):
    """表格模型，数据存储为 Task 对象列表"""
    def __init__(self, tasks):
        super().__init__()
        self._tasks = tasks

    def rowCount(self, parent=QModelIndex()):
        return len(self._tasks)

    def columnCount(self, parent=QModelIndex()):
        return 3  # 任务名、状态、进度

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        task = self._tasks[index.row()]
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return task.name
            elif col == 1:
                return task.status
            elif col == 2:
                return task.progress
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
        task = self._tasks[index.row()]
        col = index.column()
        if col == 0:
            task.name = value
        elif col == 1:
            task.status = value
        elif col == 2:
            task.progress = value
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        return True

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def insertTask(self, task):
        """添加任务"""
        row = len(self._tasks)
        self.beginInsertRows(QModelIndex(), row, row)
        self._tasks.append(task)
        self.endInsertRows()

    def removeTaskById(self, task_id):
        """通过 task_id 删除任务"""
        for row, task in enumerate(self._tasks):
            if task.task_id == task_id:
                self.beginRemoveRows(QModelIndex(), row, row)
                self._tasks.pop(row)
                self.endRemoveRows()
                return True
        return False


# ================= 进度条代理 =================
class ProgressBarDelegate(QStyledItemDelegate):
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
            QApplication.style().drawControl(QStyle.ControlElement.CE_ProgressBar, progressBarOption, painter)
        else:
            super().paint(painter, option, index)


# ================= 后台线程 =================
class WorkerThread(QThread):
    progressUpdated = Signal(str, int)  # task_id, progress

    def __init__(self, tasks):
        super().__init__()
        self._tasks = tasks
        self._running = True

    def run(self):
        while self._running:
            for task in list(self._tasks):  # 遍历任务列表
                if task.progress < 100:
                    task.progress += 1
                    self.progressUpdated.emit(task.task_id, task.progress)
            time.sleep(0.1)  # 模拟耗时任务

    def stop(self):
        self._running = False


# ================= 主窗口 =================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("任务进度表格（单线程 + 动态增删行）")

        # 初始任务
        tasks = [Task("任务A"), Task("任务B"), Task("任务C")]
        self.model = MyTableModel(tasks)

        # 表格
        self.table = QTableView()
        self.table.setModel(self.model)

        # 设置进度条代理
        delegate = ProgressBarDelegate(self.table)
        self.table.setItemDelegateForColumn(2, delegate)

        # 控制按钮
        self.btn_add = QPushButton("添加任务")
        self.btn_remove = QPushButton("删除选中任务")

        self.btn_add.clicked.connect(self.add_task)
        self.btn_remove.clicked.connect(self.remove_task)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # 后台线程
        self.worker = WorkerThread(self.model._tasks)
        self.worker.progressUpdated.connect(self.update_progress)
        self.worker.start()

    def add_task(self):
        task_name = f"任务{len(self.model._tasks)+1}"
        self.model.insertTask(Task(task_name))

    def remove_task(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return
        for index in indexes:
            task_id = self.model._tasks[index.row()].task_id
            self.model.removeTaskById(task_id)

    def update_progress(self, task_id, value):
        """根据 task_id 更新进度"""
        for row, task in enumerate(self.model._tasks):
            if task.task_id == task_id:
                self.model.setData(self.model.index(row, 2), value)
                break

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        super().closeEvent(event)


# ================= 运行 =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
