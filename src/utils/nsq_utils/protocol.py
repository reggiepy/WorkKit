# *_*coding:utf-8 *_*
# @File   : protocol.py
# @Author : Reggie
# @Time   : 2025/04/22 10:50
import re
import struct

VALID_NAME_RE = re.compile(r'^[\.a-zA-Z0-9_-]+(#ephemeral)?$')
EMPTY = b''


def _packsize(data):
    return struct.pack('>l', len(data))


def _packbody(body):
    if body is None:
        return EMPTY
    if not isinstance(body, bytes):
        raise TypeError('message body must be a byte string')
    return _packsize(body) + body


def multipublish_body(messages):
    data = EMPTY.join(_packbody(m) for m in messages)
    return _packsize(messages) + data


def _valid_name(name):
    if not 0 < len(name) < 65:
        return False
    return bool(VALID_NAME_RE.match(name))


def valid_topic_name(topic):
    return _valid_name(topic)


def valid_channel_name(channel):
    return _valid_name(channel)


def assert_valid_topic_name(topic):
    if valid_topic_name(topic):
        return
    raise ValueError('invalid topic name')


def assert_valid_channel_name(channel):
    if valid_channel_name(channel):
        return
    raise ValueError('invalid channel name')
