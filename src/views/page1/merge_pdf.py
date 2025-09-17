#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/10 14:09
# @File    : merge_pdf.py
import io
import logging
import os
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from utils.pdf_utils import pdf_to_image_bytesio, merge_invoices_top_bottom, merge_pdfs

logger = logging.getLogger("app")


class MergePDFThread(QThread):
    finishSignal = Signal(str, str, int)

    def __init__(
        self, dest_file, dest_path, pdfs, pdfs2, open_folder=True, parent=None
    ):
        super().__init__(parent)
        self.dest_file = dest_file
        self.dest_path = dest_path
        self.pdfs = pdfs
        self.pdfs2 = pdfs2
        self.open_folder = open_folder

    def run(self, /):
        try:
            dest_path = Path(self.dest_path)
            if not dest_path.exists():
                dest_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"{dest_path.as_posix()}不存在，已经创建")

            pdf_paths = self.pdfs
            # 1️⃣ 先把 PDF 渲染为图片 BytesIO
            img_bytes_list = []
            for p in pdf_paths:
                img_bytes_list.append(pdf_to_image_bytesio(p.as_posix()))

            # 2️⃣ 每两张合成一页 PDF
            single_pdfs = []
            for i in range(0, len(img_bytes_list), 2):
                img_ios = [img_bytes_list[i]]
                if i + 1 < len(img_bytes_list):
                    img_ios.append(img_bytes_list[i + 1])

                pdf_buf = io.BytesIO()
                merge_invoices_top_bottom(img_ios, pdf_buf)
                single_pdfs.append(pdf_buf)

            single_pdfs.extend(self.pdfs2)
            dest_file = self.dest_file
            if not dest_file.endswith(".pdf"):
                dest_file = dest_file + ".pdf"
            dest_file_path = dest_path / dest_file
            # 3️⃣ 合并所有 PDF
            merge_pdfs(single_pdfs, dest_file_path.as_posix())
            if self.open_folder:
                os.startfile(dest_path.as_posix())
        except Exception as e:
            logger.exception(f"合成文件失败: {e}")
            self.finishSignal.emit("", f"合成文件失败: {e}", 1)
        else:
            self.finishSignal.emit(dest_file_path.as_posix(), "success", 0)