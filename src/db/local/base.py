#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/1 14:34
# @File    : base.py
import datetime
import logging

from sqlalchemy import Column, DateTime
from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import with_loader_criteria

Base = declarative_base()

logger = logging.getLogger(__name__)


class TimestampMixin:
    """创建时间 & 更新时间"""
    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime.datetime] = mapped_column(nullable=True)
    _deleted_at_updated: bool = False

    def set_delete(self):
        if self.deleted_at is None:
            # only update deleted date if not already deleted
            self.deleted_at = datetime.datetime.now()

    def set_undelete(self):
        self.deleted_at = None


def deleted_at_set_listener(target, value, old_value, initiator):
    if isinstance(target, SoftDeleteMixin):
        target._deleted_at_updated = (value != old_value)


def before_update(mapper, connection, target):
    if isinstance(target, SoftDeleteMixin) and target._deleted_at_updated:
        if target.deleted_at:
            logger.info('%r is deleted', target)
        else:
            logger.info('%r is undeleted', target)


@event.listens_for(Base, "before_mapper_configured", propagate=True)
def on_new_class(mapper, cls_):
    if issubclass(cls_, SoftDeleteMixin):
        event.listen(cls_, "before_update", before_update)
        event.listen(cls_.deleted_at, "set", deleted_at_set_listener)


@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    skip_filter = execute_state.execution_options.get("skip_visibility_filter", False)
    if execute_state.is_select and skip_filter:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )
