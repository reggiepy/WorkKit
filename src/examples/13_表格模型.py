#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/6 21:07
# @File    : 13.py
import sys
import time
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QApplication, QTableView, QStyledItemDelegate, QStyle, QStyleOptionButton,
    QStyleOptionProgressBar, QVBoxLayout, QWidget, QMainWindow, QPushButton, QMessageBox
)
from PySide6.QtGui import QColor, QPainter
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# ==================== SQLAlchemy ====================
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String)
    progress = Column(Integer, default=0)

engine = create_engine("sqlite:///tasks.db", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# ==================== 数据模型 ====================
class SQLAlchemyTableModel(QAbstractTableModel):
    headers = ["任务名", "状态", "进度"]

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.refresh_data()

    def refresh_data(self):
        """刷新本地缓存数据"""
        self.tasks = self.session.query(Task).order_by(Task.id).all()

    def rowCount(self, parent=QModelIndex()):
        return len(self.tasks)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers) + 1  # 最后一列放按钮

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        task = self.tasks[index.row()]
        col = index.column()

        if col == len(self.headers):  # 按钮列不显示数据
            return None

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col == 0:
                return task.name
            elif col == 1:
                return task.status
            elif col == 2:
                return task.progress

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """更新本地缓存 + 提交数据库"""
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            task = self.tasks[index.row()]
            col = index.column()
            if col == 0:
                task.name = value
            elif col == 1:
                task.status = value
            elif col == 2:
                task.progress = int(value)
            self.session.commit()
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if index.column() == len(self.headers):
            return Qt.ItemFlag.ItemIsEnabled  # 按钮列不可编辑
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    return "操作"
            else:
                return f"{section + 1}"
        return None

# ==================== 后台线程 ====================
class AddTaskThread(QThread):
    """异步添加任务线程（模拟网络校验）"""
    success = Signal(object)  # 校验成功返回任务数据
    error = Signal(str)       # 校验失败返回错误消息

    def __init__(self, task_data):
        super().__init__()
        self.task_data = task_data

    def run(self):
        try:
            # 模拟网络请求/耗时校验
            time.sleep(1)
            if self.task_data["name"] == "错误":
                raise ValueError("任务名非法")
            self.success.emit(self.task_data)
        except Exception as e:
            self.error.emit(str(e))

# ==================== 按钮代理 ====================
class ButtonDelegate(QStyledItemDelegate):
    deleteClicked = Signal(int)
    upClicked = Signal(int)
    downClicked = Signal(int)

    def paint(self, painter, option, index):
        """绘制操作按钮"""
        if index.column() == index.model().columnCount() - 1:
            rect = option.rect
            button_width = rect.width() // 3

            # 删除按钮
            btn_delete = QStyleOptionButton()
            btn_delete.text = "删除"
            btn_delete.rect = rect.adjusted(0, 0, -2 * button_width, 0)
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_delete, painter)

            # 上移按钮
            btn_up = QStyleOptionButton()
            btn_up.text = "上移"
            btn_up.rect = rect.adjusted(button_width, 0, -button_width, 0)
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_up, painter)

            # 下移按钮
            btn_down = QStyleOptionButton()
            btn_down.text = "下移"
            btn_down.rect = rect.adjusted(2 * button_width, 0, 0, 0)
            QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, btn_down, painter)
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        """处理按钮点击事件"""
        if index.column() == index.model().columnCount() - 1:
            if event.type() == event.Type.MouseButtonRelease:
                rect = option.rect
                button_width = rect.width() // 3
                x = event.position().x() - rect.left()

                if x < button_width:
                    self.deleteClicked.emit(index.row())
                elif x < 2 * button_width:
                    self.upClicked.emit(index.row())
                else:
                    self.downClicked.emit(index.row())
                return True
        return super().editorEvent(event, model, option, index)

# ==================== 进度条代理 ====================
class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        """绘制进度条"""
        if index.column() == 2:
            progress = index.data()
            progress_option = QStyleOptionProgressBar()
            progress_option.rect = option.rect
            progress_option.minimum = 0
            progress_option.maximum = 100
            progress_option.progress = int(progress)
            progress_option.text = f"{progress}%"
            progress_option.textVisible = True
            QApplication.style().drawControl(QStyle.ControlElement.CE_ProgressBar, progress_option, painter)
        else:
            super().paint(painter, option, index)

# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLAlchemy 表格 + 按钮 + 进度条 + 异步增删")
        self.session = Session()

        # 初始化数据模型
        self.model = SQLAlchemyTableModel(self.session)
        self.table = QTableView()
        self.table.setModel(self.model)

        # 设置按钮代理
        self.button_delegate = ButtonDelegate(self.table)
        self.table.setItemDelegateForColumn(self.model.columnCount() - 1, self.button_delegate)
        self.button_delegate.deleteClicked.connect(self.delete_row)
        self.button_delegate.upClicked.connect(self.move_up)
        self.button_delegate.downClicked.connect(self.move_down)

        # 设置进度条代理
        self.progress_delegate = ProgressDelegate(self.table)
        self.table.setItemDelegateForColumn(2, self.progress_delegate)

        # 增加按钮添加新任务
        self.add_button = QPushButton("添加任务")
        self.add_button.clicked.connect(self.on_add_task)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.add_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 定时器更新进度条（模拟后台线程更新数据库）
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)

    # =================== 异步添加任务 ===================
    def on_add_task(self):
        """点击添加任务按钮，触发异步校验/添加"""
        task_data = {"name": f"任务{len(self.model.tasks)+1}", "status": "未完成", "progress": 0}
        self.thread = AddTaskThread(task_data)
        self.thread.success.connect(self.add_task_to_model)
        self.thread.error.connect(lambda msg: QMessageBox.warning(self, "错误", msg))
        self.thread.start()

    def add_task_to_model(self, task_data):
        """线程返回成功信号后，将任务加入模型并提交数据库"""
        task = Task(**task_data)
        self.session.add(task)
        self.session.commit()
        self.model.refresh_data()
        self.model.layoutChanged.emit()

    # =================== 删除 / 上移 / 下移 ===================
    def delete_row(self, row):
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除第 {row + 1} 行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            task = self.model.tasks[row]
            self.session.delete(task)
            self.session.commit()
            self.model.refresh_data()
            self.model.layoutChanged.emit()

    def move_up(self, row):
        if row <= 0:
            return
        self.model.tasks[row-1].id, self.model.tasks[row].id = self.model.tasks[row].id, self.model.tasks[row-1].id
        self.session.commit()
        self.model.refresh_data()
        self.model.layoutChanged.emit()

    def move_down(self, row):
        if row >= len(self.model.tasks) - 1:
            return
        self.model.tasks[row+1].id, self.model.tasks[row].id = self.model.tasks[row].id, self.model.tasks[row+1].id
        self.session.commit()
        self.model.refresh_data()
        self.model.layoutChanged.emit()

    # =================== 模拟后台更新进度 ===================
    def update_progress(self):
        """定时器模拟后台更新进度"""
        updated = False
        for task in self.model.tasks:
            if task.progress < 100:
                task.progress += 1
                updated = True
        if updated:
            self.session.commit()
            self.model.layoutChanged.emit()

# ==================== 运行 ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
