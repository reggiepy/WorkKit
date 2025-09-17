# *_*coding:utf-8 *_*
# @File   : main.py
# @Author : Reggie
# @Time   : 2025/08/27 18:08
import logging
import sys
import traceback

from PySide6.QtWidgets import QApplication

from core import settings
from core.logger import init_logger
from db.init_db import init_local_db
from version import version_info
from views.main_window import MainWindow

logger = logging.getLogger("app")


# 设置异常处理
def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"未处理的异常:\n{error_msg}")

    # 尝试显示错误对话框
    try:
        from PySide6.QtWidgets import QMessageBox, QApplication

        if QApplication.instance():
            QMessageBox.critical(
                None,
                "程序错误",
                f"程序遇到未处理的错误:\n{str(exc_value)}\n\n"
                "请联系技术支持并提供错误信息。",
            )
    except:
        pass


if __name__ == "__main__":
    init_logger(settings.LOG_CONFIG)
    init_local_db()
    # 设置全局异常处理器
    sys.excepthook = handle_exception
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        main_windows = MainWindow()
        main_windows.show()
        exit_code = app.exec()
        sys.exit(exit_code)
    except Exception as e:
        error_msg = f"应用程序启动过程中出现异常: {str(e)}\n\n错误详情:\n{traceback.format_exc()}"
        logger.error(error_msg)
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动错误", f"程序启动失败:\n{str(e)}")
        except:
            input(f"{error_msg}\n\n按Enter键退出...")
        sys.exit(1)
