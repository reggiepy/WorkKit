#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/2 17:48
# @File    : common.py
import logging

_logger = logging.getLogger("app")


def parse_product_info(product_info, logger=None):
    logger = logger if logger else _logger
    result = {}
    products = product_info.split("，")
    for product in products:
        product_split = product.split("/")
        if len(product_split) != 2:
            logger.error(f"输入有误: {product}")
            continue
        product_id, quantity = product_split
        if not quantity.isdigit():
            logger.error(f"输入有误, 数量应为一个数字: {quantity}")
            continue
        quantity = int(quantity)
        if quantity <= 0:
            logger.error("输入错误数量应该大于0")
            continue
        if product_id not in result:
            result[product_id] = int(quantity)
    return result


def unparse_product_info(product_info):
    product = []
    for product_id, quantity in product_info.items():
        product.append(f"{product_id}/{quantity}")

    return "，".join(product)