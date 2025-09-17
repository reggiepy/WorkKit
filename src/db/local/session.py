#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/1 14:35
# @File    : session.py
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.settings import DB_URI

engine = create_engine(DB_URI, future=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def session_factory():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
