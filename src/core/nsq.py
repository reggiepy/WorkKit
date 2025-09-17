#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : wt
# @Time    : 2025/9/7 10:45
# @File    : nsq.py
from core import settings
from utils.nsq_utils.nsqd import NsqdHTTPClient


def get_nsqd_http_client() -> NsqdHTTPClient:
    return NsqdHTTPClient(settings.NSQD_HTTP_HOST, settings.NSQD_HTTP_PORT)
