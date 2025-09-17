#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/9 09:52
# @File    : alembic_utils.py
import os

from alembic import command
from alembic.config import Config


def get_alembic_config(base_dir):
    """加载 Alembic 配置"""
    config_file_path = os.path.join(base_dir, 'alembic.ini')
    alembic_cfg = Config(config_file_path)
    # 这里可以动态覆盖，比如设置 sqlalchemy.url
    # alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///local.db")
    return alembic_cfg


def alembic_upgrade(alembic_cfg, revision="head"):
    """升级到指定版本，默认升级到最新"""
    command.upgrade(alembic_cfg, revision)


def alembic_downgrade(alembic_cfg, revision="-1"):
    """回退到指定版本，默认回退 1 个版本"""
    command.downgrade(alembic_cfg, revision)


def alembic_stamp(alembic_cfg, revision="head"):
    """
    将数据库标记为指定版本（默认 head），不会执行迁移
    禁止 Alembic 修改全局日志
    """
    command.stamp(alembic_cfg, revision)


def alembic_revision(alembic_cfg, message="auto", autogenerate=True):
    """生成新的迁移脚本"""
    command.revision(alembic_cfg, message=message, autogenerate=autogenerate)


def alembic_show(alembic_cfg, revision="head"):
    """显示某个版本信息"""
    command.show(alembic_cfg, revision)


def alembic_history(alembic_cfg):
    """显示迁移历史"""
    command.history(alembic_cfg)


def alembic_current(alembic_cfg):
    """显示当前数据库版本"""
    command.current(alembic_cfg)
