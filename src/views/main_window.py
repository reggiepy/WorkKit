# *_*coding:utf-8 *_*
# @File   : main_window.py
# @Author : Reggie
# @Time   : 2025/08/28 09:27
import datetime
import logging
import os
from pathlib import Path
from typing import Optional

import fitz
from PySide6.QtCore import QUrl, QThread
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog,
)

import version
from core.settings import BASE_DIR
from ui.tools import Ui_MainWindow
from utils.icon_utils import generate_icon, icon_shape
from utils.sound_utils import generate_sound
from views.loading import LoadingDialog
from views.page1.invoice_pdf import SinglePagePdfTableModel, SinglePagePdfDropFilter
from views.page1.merge_pdf import MergePDFThread
from views.page1.single_page_pdf import (
    InvoicePdfTableModel,
    InvoicePdfButtonDelegate,
    InvoicePdfDropFilter,
)

logger = logging.getLogger("app")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        title = f"工作工具包 v{version.VERSION}"
        self.setWindowTitle(title)
        # 设置基础缓存目录
        home_dir = os.path.expanduser("~")
        self.cache_dir = Path(home_dir) / ".yfsteel2"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 设置成功提示音文件路径
        self.success_sound_file = self.cache_dir / "success_sound.wav"
        self.meta_file_path = self.cache_dir / "config.json"

        # 设置应用图标
        self.setup_app_icon()

        # 设置音频
        self.setup_audio()

        # 显示欢迎消息
        self.statusBar().showMessage("欢迎使用")

        # 报销合并发票 - 发票表
        self.invoicePdfTableModel = InvoicePdfTableModel()
        self.invoicePdfTableView.setModel(self.invoicePdfTableModel)
        self.invoicePdfTableView.installEventFilter(
            InvoicePdfDropFilter(self.invoicePdfTableModel, self.invoicePdfTableView)
        )
        self.invoicePdfTableView.setColumnHidden(1, True)

        self.invoicePdfButtonDelegate = InvoicePdfButtonDelegate(
            self.invoicePdfTableView
        )
        self.invoicePdfButtonDelegate.deleteClicked.connect(self.invoicePdfTableModel.on_delete_row)
        self.invoicePdfButtonDelegate.upClicked.connect(self.invoicePdfTableModel.on_move_up)
        self.invoicePdfButtonDelegate.downClicked.connect(self.invoicePdfTableModel.on_move_down)
        self.invoicePdfTableView.setItemDelegateForColumn(
            5, self.invoicePdfButtonDelegate
        )

        # 报销合并发票 - 单页pdf表
        self.singlePagePdfTableModel = SinglePagePdfTableModel()
        self.singlePagePdfTableView.setModel(self.singlePagePdfTableModel)
        self.singlePagePdfTableView.installEventFilter(
            SinglePagePdfDropFilter(
                self.singlePagePdfTableModel, self.singlePagePdfTableView
            )
        )
        self.singlePagePdfTableView.setColumnHidden(1, True)

        self.singlePagePdfButtonDelegate = InvoicePdfButtonDelegate(
            self.singlePagePdfTableView
        )
        self.singlePagePdfButtonDelegate.deleteClicked.connect(self.singlePagePdfTableModel.on_delete_row)
        self.singlePagePdfButtonDelegate.upClicked.connect(self.singlePagePdfTableModel.on_move_up)
        self.singlePagePdfButtonDelegate.downClicked.connect(self.singlePagePdfTableModel.on_move_down)
        self.singlePagePdfTableView.setItemDelegateForColumn(
            5, self.singlePagePdfButtonDelegate
        )

        # # 遮罩（进度提示）
        self.loading_progress = LoadingDialog(self, "初始化...")

        self.startpushButton.clicked.connect(self.on_start)
        self.startThread: Optional[QThread] = None

        # 按钮
        self.outputFileNamelineEdit.setText(f"merge_pdf_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
        self.clearInvoicePdfpushButton.clicked.connect(lambda: self.on_clear_page_pdf(self.invoicePdfTableModel))
        self.clearSinglePagePdfpushButton.clicked.connect(lambda: self.on_clear_page_pdf(self.singlePagePdfTableModel))
        self.addInvoicePdfpushButton.clicked.connect(lambda: self.on_add_file(self.invoicePdfTableModel))
        self.addSinglePagePdfpushButton.clicked.connect(lambda: self.on_add_file(self.singlePagePdfTableModel))

    def on_clear_page_pdf(self, model):
        reply = QMessageBox.question(
            self,
            "删除",
            f"确定清空所有文件吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            model.on_files_loaded([])

    def on_add_file(self, model):
        """打开文件选择对话框并添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择 PDF 文件",
            "",
            "PDF 文件 (*.pdf)"
        )
        for file_path in files:
            file_info = self.load_pdf_info(file_path)
            model.on_file_inserted(file_info)

    def load_pdf_info(self, file_path: str) -> dict:
        """解析 PDF 文件并返回字典信息"""
        doc = fitz.open(file_path)
        file_info = {
            "filename": Path(file_path).name,
            "filepath": file_path,
            "pagesize": doc.page_count,
            "file_range": f"1-{doc.page_count}",
            "status": "加载成功"
        }
        doc.close()
        return file_info

    def on_start(self):
        if self.startThread is not None:
            return
        self.loading_progress.show("开始合并...")
        pdfs = [Path(f["filepath"]) for f in self.invoicePdfTableModel.files]
        pdfs2 = [Path(f["filepath"]) for f in self.singlePagePdfTableModel.files]
        if not any([pdfs, pdfs2]):
            QMessageBox.warning(
                self,
                "警告",
                f"请传入一个文件",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            return
        dest_file = self.outputFileNamelineEdit.text()
        dest_path = self.outputFilePathlineEdit.text()
        open_folder = self.openExplorercheckBox.isChecked()
        self.startThread = MergePDFThread(
            dest_file,
            dest_path,
            pdfs,
            pdfs2,
            open_folder=open_folder
        )
        self.startThread.finishSignal.connect(self.on_start_finish)
        self.startThread.start()

    def on_start_finish(self, file_path, message, rc):
        if rc:
            reply = QMessageBox.critical(
                self,
                "合并异常",
                message,
                QMessageBox.StandardButton.Ok,
            )
            # if reply == QMessageBox.StandardButton.Ok:
            #     self.close()
        self.startThread = None
        self.outputFileNamelineEdit.setText(f"merge_pdf_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
        self.loading_progress.close()

    def setup_audio(self):
        """初始化音频"""
        self.audio_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_player.setAudioOutput(self.audio_output)

        # 设置音量 (0.0 - 1.0)
        self.audio_output.setVolume(0.5)

        # 如果文件不存在，尝试生成
        if (
                not self.success_sound_file.exists()
                or self.success_sound_file.stat().st_size == 0
        ):
            _, msg, rc = generate_sound(self.success_sound_file.as_posix())
            if rc:
                logger.error(msg)
            else:
                logger.info(f"生成音频成功")
        logger.info("音频系统已初始化")

    def play_success_sound(self):
        """播放成功提示音"""
        logger.info("播放成功提示音")
        try:
            # 检查音频文件是否存在且有效
            if all(
                    [
                        self.success_sound_file,
                        self.success_sound_file.exists(),
                        self.success_sound_file.stat().st_size != 0,
                    ]
            ):
                if (
                        self.audio_player.mediaStatus()
                        == QMediaPlayer.MediaStatus.LoadedMedia
                ):
                    if (
                            self.audio_player.playbackState()
                            != QMediaPlayer.PlaybackState.PlayingState
                    ):
                        # 设置音频源并播放
                        self.audio_player.setSource(
                            QUrl.fromLocalFile(self.success_sound_file)
                        )
                        self.audio_player.play()
                        self.statusBar().showMessage("正在播放抢单成功提示音...")
            else:
                self.statusBar().showMessage("提示音文件不存在或无效，尝试重新生成...")
                _, msg, rc = generate_sound(self.success_sound_file)
                if rc:
                    logger.info(msg)
                # 重试播放
                if not any(
                        [
                            not self.success_sound_file,
                            self.success_sound_file.exists(),
                            self.success_sound_file.stat().st_size == 0,
                        ]
                ):
                    if (
                            self.audio_player.mediaStatus()
                            == QMediaPlayer.MediaStatus.LoadedMedia
                    ):
                        if (
                                self.audio_player.playbackState()
                                != QMediaPlayer.PlaybackState.PlayingState
                        ):
                            self.audio_player.setSource(
                                QUrl.fromLocalFile(self.success_sound_file)
                            )
                            self.audio_player.play()
                            self.statusBar().showMessage(
                                "已自动生成并播放抢单成功提示音"
                            )
                else:
                    self.statusBar().showMessage("无法生成或播放提示音")
        except Exception as e:
            self.statusBar().showMessage(f"播放提示音时出错: {str(e)}")
            # 即使音频播放失败，也不要让程序崩溃

    def setup_app_icon(self):
        """设置应用程序图标"""
        try:
            # 尝试导入图标模块
            png_file_path, ico_file_path = generate_icon(
                icon_shape, BASE_DIR / "resources"
            )
            if ico_file_path and ico_file_path.exists():
                self.setWindowIcon(QIcon(ico_file_path.as_posix()))
                self.statusBar().showMessage("应用图标已设置")
                return

            # 尝试查找已存在的图标文件
            possible_icon_paths = [
                BASE_DIR / "resources" / "app_icon.ico",
                BASE_DIR / "resources" / "app_icon.png",
            ]

            for icon_path in possible_icon_paths:
                if icon_path.exists():
                    try:
                        self.setWindowIcon(QIcon(icon_path.as_posix()))
                        logger.info(f"使用已存在的图标: {icon_path}")
                        return
                    except Exception as e:
                        logger.exception(f"设置图标失败: {e}")
                        continue

            # 如果没有找到图标文件，使用默认图标
            self.statusBar().showMessage("使用系统默认图标")

        except Exception as e:
            logger.exception(f"设置应用图标时出错: {str(e)}")
            # 确保不会因为图标问题导致程序崩溃

    def cleanup(self):
        logger.info("正在清理线程...")
        if self.startThread:
            self.startThread.quit()
            self.startThread.wait()

    def closeEvent(self, event):
        self.cleanup()
        event.accept()
