# *_*coding:utf-8 *_*
# @File   : 1.py
# @Author : Reggie
# @Time   : 2025/07/23 15:41
import io
import logging
import time

import fitz  # PyMuPDF
from PIL import Image, ImageChops
from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


# ========= 工具函数 =========

def trim_white_border(img: Image.Image, bg_color="white") -> Image.Image:
    """自动裁剪图片四周的纯白空白区域"""
    bg = Image.new(img.mode, img.size, bg_color)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    return img.crop(bbox) if bbox else img


def pdf_to_image_bytesio(pdf_path, page_num=0, dpi=150) -> io.BytesIO:
    """PDF → 渲染第一页 → JPEG BytesIO"""
    t0 = time.time()
    logger.info(f"渲染 PDF → 图片: {pdf_path}")
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    zoom = dpi / 72.0  # 默认 72dpi → 150dpi
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes(output="jpeg")
    doc.close()
    logger.info(f"✅ 渲染完成，用时 {time.time() - t0:.2f}s")
    return io.BytesIO(img_bytes)


def pdf_to_image_savefile(pdf_path, save_path, page_num=0, dpi=150):
    """PDF 渲染第 page_num 页，保存为图片文件"""
    t0 = time.time()
    logger.info(f"渲染 PDF → 图片并保存: {pdf_path}")
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    pix.save(save_path)
    doc.close()
    logger.info(f"✅ 图片保存到: {save_path}，耗时 {time.time() - t0:.2f}s")


def merge_invoices_top_bottom(img_ios, output_stream: io.BytesIO, margin_mode="none"):
    """
    将 1~2 张图片上下合并到 1 页 PDF 并写入 output_stream

    :param img_ios: list[BytesIO | PIL.Image]
        - 图片列表，可传 1 或 2 张图片
        - 如果是 BytesIO，会自动 Image.open()，如果是 PIL.Image 直接使用
    :param output_stream: io.BytesIO
        - 输出的 PDF 文件流
    :param margin_mode: str
        - "none"   无边距（图片尽可能铺满半页）
        - "narrow" 窄边距（大约 7mm）
        - "wide"   宽边距（大约 17mm）

    :return: None
        - 函数执行后会将合并好的 PDF 内容写入 output_stream
    """
    import time

    t0 = time.time()
    logger.info("开始合并 1~2 张图片到一页 PDF ...")

    # A4 页面宽高（pt 单位）
    page_width, page_height = A4
    half_height = page_height / 2  # 半页高度

    # 创建临时缓冲区，ReportLab 会先写入这里，再写到 output_stream
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    def draw_img(img, y_offset, max_height, margin_mode="none"):
        """
        内部工具函数：绘制单张图片到指定区域

        :param img: PIL.Image
        :param y_offset: Y 坐标偏移，表示绘制区域的起始高度（用于区分上/下半页）
        :param max_height: 允许绘制的最大高度（一般是半页）
        :param margin_mode: 控制边距模式（none / narrow / wide）
        """
        t_start = time.time()

        # 1️⃣ 根据 margin_mode 选择边距大小（pt）
        if margin_mode == "none":
            margin = 0  # 无边距，尽量铺满区域
        elif margin_mode == "narrow":
            margin = 20  # 约 7mm
        elif margin_mode == "wide":
            margin = 50  # 约 17mm
        else:
            margin = 0  # 默认无边距

        # 2️⃣ 计算可用绘制区域（宽度、高度）
        usable_width = page_width - 2 * margin  # 除去左右边距
        usable_height = max_height - 2 * margin  # 除去上下边距

        # 3️⃣ 获取图片像素尺寸（px）
        img_w, img_h = img.size

        # 4️⃣ 计算缩放比例：
        #     - scale_w：适配宽度的比例
        #     - scale_h：适配高度的比例
        #     - 取最小值保证不会超出边界
        scale_w = usable_width / img_w
        scale_h = usable_height / img_h
        scale = min(scale_w, scale_h)

        # 5️⃣ 计算最终绘制宽高（pt）
        draw_w = img_w * scale
        draw_h = img_h * scale

        # 6️⃣ 计算居中偏移（保证图片水平居中，竖直方向同样居中）
        x_offset = margin + (usable_width - draw_w) / 2
        y_offset = y_offset + margin + (usable_height - draw_h) / 2

        # 7️⃣ 在 PDF 页面绘制图片
        c.drawInlineImage(img, x_offset, y_offset, width=draw_w, height=draw_h)

        logger.info(f"绘制图片耗时: {time.time() - t_start:.3f}s")

    # 处理第 1 张图片（上半页）
    t_img1_start = time.time()
    if len(img_ios) >= 1:
        # 如果传入的是 BytesIO，则打开成 PIL.Image；否则直接使用
        img1 = Image.open(img_ios[0]) if not isinstance(img_ios[0], Image.Image) else img_ios[0]
        # 如果想裁剪白边可以打开这一行：
        # img1 = trim_white_border(img1)

        logger.info(f"打开第1张图片耗时: {time.time() - t_img1_start:.3f}s")
        draw_img(img1, half_height, half_height, margin_mode)

    # 处理第 2 张图片（下半页）
    if len(img_ios) >= 2:
        t_img2_start = time.time()
        img2 = Image.open(img_ios[1]) if not isinstance(img_ios[1], Image.Image) else img_ios[1]
        # img2 = trim_white_border(img2)

        logger.info(f"打开第2张图片耗时: {time.time() - t_img2_start:.3f}s")
        draw_img(img2, 0, half_height, margin_mode)

        # 画分割虚线（只有上下都有图才画）
        c.setDash(5, 5)
        c.setLineWidth(1)
        c.line(0, half_height, page_width, half_height)
        c.setDash()

    # 保存 PDF 到缓冲区
    t_save_start = time.time()
    c.showPage()
    c.save()
    logger.info(f"保存 PDF 耗时: {time.time() - t_save_start:.3f}s")

    # 把缓冲区数据写到最终的 output_stream
    buf.seek(0)
    output_stream.write(buf.read())
    output_stream.seek(0)

    logger.info(f"✅ 合并完成，总耗时 {time.time() - t0:.3f}s")


def merge_pdfs(pdf_streams, output_file):
    """合并多个 PDF BytesIO，输出一个 PDF 文件"""
    t0 = time.time()
    logger.info(f"开始合并 {len(pdf_streams)} 个 PDF → {output_file}")

    writer = PdfWriter()
    for idx, pdf_stream in enumerate(pdf_streams, 1):
        reader = PdfReader(pdf_stream)
        for page in reader.pages:
            writer.add_page(page)
        logger.debug(f"已添加第 {idx}/{len(pdf_streams)} 个 PDF")

    with open(output_file, "wb") as f:
        writer.write(f)

    logger.info(f"✅ 最终合并完成：{output_file}，总耗时 {time.time() - t0:.2f}s")
