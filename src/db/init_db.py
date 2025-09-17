# *_*coding:utf-8 *_*
# @File   : init_db.py
# @Author : Reggie
# @Time   : 2025/07/23 22:07
import logging

from core.settings import ALEMBIC_CONFIG_PATH, ALEMBIC_SCRIPT_LOCATION
from db.local.session import session_factory
from utils.alembic_utils import alembic_upgrade, get_alembic_config, alembic_stamp
from models.account import Account

logger = logging.getLogger("app")


def init_local_db():
    alembic_cfg = get_alembic_config(ALEMBIC_CONFIG_PATH)
    alembic_cfg.set_main_option("script_location", ALEMBIC_SCRIPT_LOCATION.as_posix())
    # alembic_stamp(alembic_cfg)
    alembic_upgrade(alembic_cfg)
    with session_factory() as session:
        # AccountController.reset_account(session)
        pass