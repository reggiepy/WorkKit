#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/7 09:37
# @File    : 14.py
import sys
import time
from PySide6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex,
    QObject, Signal, Slot, QThread, QTimer
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QLineEdit, QMessageBox, QStyledItemDelegate,
    QStyle, QStyleOptionButton, QStyleOptionProgressBar
)
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# ==================== SQLAlchemy ORM ====================
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    progress = Column(Integer, default=0)


engine = create_engine("sqlite:///tasks.db", echo=False, future=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, expire_on_commit=False)

# ==================== Repo (运行在 QThread) ====================
class TaskRepository(QObject):
    tasks_loaded = Signal(list)
    task_inserted = Signal(dict)
    task_deleted = Signal(int)
    task_progress_updated = Signal(int, int)  # task_id, progress

    def __init__(self):
        super().__init__()
        self.Session = Session

    @Slot()
    def load_all(self):
        with self.Session() as session:
            rows = session.query(Task).order_by(Task.id).all()
            tasks = [{"id": t.id, "name": t.name, "progress": t.progress} for t in rows]
            self.tasks_loaded.emit(tasks)

    @Slot(str)
    def insert_task(self, name: str):
        time.sleep(5)
        with self.Session() as session:
            task = Task(name=name)
            session.add(task)
            session.commit()
            self.task_inserted.emit({"id": task.id, "name": task.name, "progress": task.progress})

    @Slot(int)
    def delete_task(self, task_id: int):
        time.sleep(5)
        with self.Session() as session:
            task = session.get(Task, task_id)
            if task:
                session.delete(task)
                session.commit()
                self.task_deleted.emit(task_id)

    @Slot()
    def update_progress(self):
        """模拟后台任务进度更新"""
        time.sleep(5)
        with self.Session() as session:
            tasks = session.query(Task).all()
            for task in tasks:
                # 确保 progress 是整数
                if task.progress is None:
                    task.progress = 0
                if task.progress < 100:
                    task.progress += 1
                    session.commit()
                    self.task_progress_updated.emit(task.id, task.progress)

# ==================== 表格模型 ====================
class TaskTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        # 存储任务数据的列表，每个任务是一个字典，包含 id、name、progress 等字段
        self.tasks = []  # 示例：{"id": 1, "name": "任务A", "progress": 50}

    # 返回表格行数，即任务数量
    def rowCount(self, parent=QModelIndex()):
        return len(self.tasks)

    # 返回表格列数
    def columnCount(self, parent=QModelIndex()):
        return 4  # 包含 id（隐藏列）、任务名、进度、操作列

    # 返回单元格数据
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        task = self.tasks[index.row()]  # 获取对应行的任务
        col = index.column()            # 获取列号
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return task["id"]       # 第一列：任务 ID
            elif col == 1:
                return task["name"]     # 第二列：任务名
            elif col == 2:
                return task["progress"] # 第三列：任务进度
        return None

    # 返回单元格的标志（可选中、可编辑等）
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if index.column() == 3:
            # 操作列只允许点击，不可编辑
            return Qt.ItemFlag.ItemIsEnabled
        # 其他列可选中、可编辑
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    # 表头数据
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            # 水平表头
            return ["ID", "任务名", "进度", "操作"][section]
        # 垂直表头显示行号
        return str(section + 1)

    # ---- 槽函数，用于接收外部信号更新模型 ----

    # 当任务列表加载完成时，刷新整个表格
    def on_tasks_loaded(self, tasks):
        self.beginResetModel()  # 通知视图开始重置
        self.tasks = tasks
        self.endResetModel()    # 通知视图结束重置

    # 当插入新任务时，追加到表格末尾
    def on_task_inserted(self, task):
        row = len(self.tasks)  # 新行索引
        self.beginInsertRows(QModelIndex(), row, row)  # 通知视图插入行
        self.tasks.append(task)
        self.endInsertRows()    # 通知视图插入完成

    # 当删除任务时，根据 task_id 找到行并删除
    def on_task_deleted(self, task_id):
        row = next((i for i, t in enumerate(self.tasks) if t["id"] == task_id), -1)
        if row >= 0:
            self.beginRemoveRows(QModelIndex(), row, row)  # 通知视图开始删除行
            del self.tasks[row]
            self.endRemoveRows()  # 通知视图删除完成

    # 当任务进度更新时，刷新对应单元格
    def on_task_progress_updated(self, task_id, progress):
        row = next((i for i, t in enumerate(self.tasks) if t["id"] == task_id), -1)
        if row >= 0:
            self.tasks[row]["progress"] = progress  # 更新数据
            idx = self.index(row, 2)  # 获取进度列的 QModelIndex
            # 通知视图指定单元格的数据已改变
            self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole])

# ==================== 按钮代理 ====================
class ButtonDelegate(QStyledItemDelegate):
    deleteClicked = Signal(int)
    upClicked = Signal(int)
    downClicked = Signal(int)

    def paint(self, painter, option, index):
        if index.column() == 3:
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
        if index.column() == 3 and event.type() == event.Type.MouseButtonRelease:
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

# ==================== 进度条代理 ====================
class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 2:
            progress = index.data()
            opt = QStyleOptionProgressBar()
            opt.rect = option.rect
            opt.minimum = 0
            opt.maximum = 100
            opt.progress = int(progress) if progress else 0
            opt.text = f"{progress}%"
            opt.textVisible = True
            QApplication.style().drawControl(QStyle.ControlElement.CE_ProgressBar, opt, painter)
        else:
            super().paint(painter, option, index)

# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self, repo, model):
        super().__init__()
        self.repo = repo
        self.model = model
        self.setWindowTitle("SQLAlchemy + QThread Repo + QTableView")

        self.table = QTableView()
        self.table.setModel(model)

        # 隐藏ID列
        self.table.setColumnHidden(0, True)

        # 设置按钮代理
        self.btn_delegate = ButtonDelegate(self.table)
        self.table.setItemDelegateForColumn(3, self.btn_delegate)
        self.btn_delegate.deleteClicked.connect(self.delete_row)
        self.btn_delegate.upClicked.connect(self.move_up)
        self.btn_delegate.downClicked.connect(self.move_down)

        # 设置进度条代理
        self.progress_delegate = ProgressDelegate(self.table)
        self.table.setItemDelegateForColumn(2, self.progress_delegate)

        # 增加任务
        self.input = QLineEdit()
        self.input.setPlaceholderText("输入任务名称")
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_task)
        hbox = QHBoxLayout()
        hbox.addWidget(self.input)
        hbox.addWidget(add_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(hbox)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 启动后台定时器模拟进度
        self.timer = QTimer()
        self.timer.timeout.connect(repo.update_progress)
        self.timer.start(6000)

        # 延迟加载数据，避免卡死
        QTimer.singleShot(0, repo.load_all)

    def add_task(self):
        name = self.input.text().strip()
        if name:
            self.repo.insert_task(name)
            self.input.clear()

    def delete_row(self, row):
        task_id = self.model.tasks[row]["id"]
        reply = QMessageBox.question(
            self, "删除", f"确定删除该任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.repo.delete_task(task_id)

    def move_up(self, row):
        if row <= 0:
            return
        self.model.tasks[row - 1], self.model.tasks[row] = self.model.tasks[row], self.model.tasks[row - 1]
        self.model.layoutChanged.emit()

    def move_down(self, row):
        if row >= len(self.model.tasks) - 1:
            return
        self.model.tasks[row + 1], self.model.tasks[row] = self.model.tasks[row], self.model.tasks[row + 1]
        self.model.layoutChanged.emit()

# ==================== 程序启动 ====================
def main():
    app = QApplication(sys.argv)

    repo = TaskRepository()
    thread = QThread()
    repo.moveToThread(thread)
    thread.start()

    model = TaskTableModel()
    # 信号绑定
    repo.tasks_loaded.connect(model.on_tasks_loaded)
    repo.task_inserted.connect(model.on_task_inserted)
    repo.task_deleted.connect(model.on_task_deleted)
    repo.task_progress_updated.connect(model.on_task_progress_updated)

    window = MainWindow(repo, model)
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
