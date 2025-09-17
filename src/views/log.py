# *_*coding:utf-8 *_*
# @File   : lgo.py
# @Author : Reggie
# @Time   : 2025/08/28 12:47
import logging

from PySide6.QtCore import QObject, Signal


class QtHandler(logging.Handler, QObject):
    log_signal = Signal(str)

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)  # 发射信号
