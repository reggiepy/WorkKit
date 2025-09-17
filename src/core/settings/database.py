#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/1 14:41
# @File    : database.py
from .base import CACHE_DIR

DB_TYPE = "sqlite"
DB_URI = f"sqlite:///{CACHE_DIR / 'database.db'}"
