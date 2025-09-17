# *_*coding:utf-8 *_*
# @File   : base.py
# @Author : Reggie
# @Time   : 2025/08/28 12:38
import os
from pathlib import Path
from .. import const

BASE_DIR = const.BASE_DIR
PROJECT_DIR = const.PROJECT_DIR

HOME_DIR = os.path.expanduser("~")
CACHE_DIR = Path(HOME_DIR) / ".workkit"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
