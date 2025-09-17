# *_*coding:utf-8 *_*
# @File   : nsqd.py
# @Author : Reggie
# @Time   : 2025/04/22 10:51
import requests

from . import errors, protocol


class NsqdHTTPClient(object):
    def __init__(self, host='localhost', port=4151, **kwargs):
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': kwargs.get('useragent', 'nsq-client/1.0')
        })
        self.session.auth = kwargs.get('auth', None)

    def _request(self, method, endpoint, fields=None, body=None):
        url = f"{self.base_url}{endpoint}"
        if method.upper() == 'GET':
            resp = self.session.get(url, params=fields)
        else:
            resp = self.session.post(url, params=fields, data=body)

        resp.raise_for_status()
        return resp.text if 'text' in resp.headers.get('Content-Type', '') else resp.json()

    def publish(self, topic, data, defer=None):
        protocol.assert_valid_topic_name(topic)
        fields = {'topic': topic}
        if defer is not None:
            fields['defer'] = str(defer)
        return self._request('POST', '/pub', fields=fields, body=data)

    def _validate_mpub_message(self, message):
        if b'\n' not in message:
            return message
        raise errors.NSQException('newlines are not allowed in http multipublish')

    def multipublish(self, topic, messages, binary=False):
        protocol.assert_valid_topic_name(topic)
        fields = {'topic': topic}
        if binary:
            fields['binary'] = 'true'
            body = protocol.multipublish_body(messages)
        else:
            body = b'\n'.join(self._validate_mpub_message(m) for m in messages)
        return self._request('POST', '/mpub', fields=fields, body=body)

    def create_topic(self, topic):
        protocol.assert_valid_topic_name(topic)
        return self._request('POST', '/topic/create', fields={'topic': topic})

    def delete_topic(self, topic):
        protocol.assert_valid_topic_name(topic)
        return self._request('POST', '/topic/delete', fields={'topic': topic})

    def create_channel(self, topic, channel):
        protocol.assert_valid_topic_name(topic)
        protocol.assert_valid_channel_name(channel)
        return self._request('POST', '/channel/create',
                             fields={'topic': topic, 'channel': channel})

    def delete_channel(self, topic, channel):
        protocol.assert_valid_topic_name(topic)
        protocol.assert_valid_channel_name(channel)
        return self._request('POST', '/channel/delete',
                             fields={'topic': topic, 'channel': channel})

    def empty_topic(self, topic):
        protocol.assert_valid_topic_name(topic)
        return self._request('POST', '/topic/empty', fields={'topic': topic})

    def empty_channel(self, topic, channel):
        protocol.assert_valid_topic_name(topic)
        protocol.assert_valid_channel_name(channel)
        return self._request('POST', '/channel/empty',
                             fields={'topic': topic, 'channel': channel})

    def pause_topic(self, topic):
        protocol.assert_valid_topic_name(topic)
        return self._request('POST', '/topic/pause', fields={'topic': topic})

    def unpause_topic(self, topic):
        protocol.assert_valid_topic_name(topic)
        return self._request('POST', '/topic/unpause', fields={'topic': topic})

    def pause_channel(self, topic, channel):
        protocol.assert_valid_topic_name(topic)
        protocol.assert_valid_channel_name(channel)
        return self._request('POST', '/channel/pause',
                             fields={'topic': topic, 'channel': channel})

    def unpause_channel(self, topic, channel):
        protocol.assert_valid_topic_name(topic)
        protocol.assert_valid_channel_name(channel)
        return self._request('POST', '/channel/unpause',
                             fields={'topic': topic, 'channel': channel})

    def stats(self, topic=None, channel=None, text=False):
        fields = {'format': 'text' if text else 'json'}
        if topic:
            protocol.assert_valid_topic_name(topic)
            fields['topic'] = topic
        if channel:
            protocol.assert_valid_channel_name(channel)
            fields['channel'] = channel
        return self._request('GET', '/stats', fields=fields)

    def ping(self):
        return self._request('GET', '/ping')

    def info(self):
        return self._request('GET', '/info')
