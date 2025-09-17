#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/1 14:52
# @File    : account.py
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Enum, Integer, Text, Boolean

from db.local.base import Base as LocalBase, TimestampMixin, SoftDeleteMixin


class CategoryEnum(PyEnum):
    SCAN = "scan"
    SNATCH = "snatch"


class Account(LocalBase, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), comment="用户名")
    password = Column(String(64), comment="密码")
    category = Column(Enum(CategoryEnum), nullable=False, comment="类型")
    # 抢单配置
    cart_expire_time = Column(Integer, comment="购物车过期时间")
    product_info = Column(String(255), comment="要购买的产品")
    success_count = Column(Integer, default=0, comment="success_count")
    default_contract = Column(String(255), default=0, comment="success_count")
    is_finish = Column(Boolean, default=False, comment="是否已经完成")
    # 登陆配置
    user_info = Column(Text, comment="用户信息")
    contracts = Column(Text, comment="协议")
    token = Column(String(64), comment="token")
    cookies = Column(Text, comment="cookies")
