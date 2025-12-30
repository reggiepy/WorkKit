#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/1 14:52
# @File    : account.py
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Enum, Integer, Text, Boolean

from db.local.base import Base as LocalBase, TimestampMixin, SoftDeleteMixin
