# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/2/7 16:37
import json
import logging
import logging.config
import os


def init_logger(config, env_key='LOG_CFG'):
    """Build and return the logger.

    env_key define the env var where a path to a specific JSON logger
            could be defined

    :return: logger -- Logger instance
    """
    _logger = logging.getLogger()

    # Check if a specific configuration is available
    user_file = os.getenv(env_key, None)
    if user_file and os.path.exists(user_file):
        # A user file as been defined. Use it...
        with open(user_file, 'rt') as f:
            config = json.load(f)

    # Load the configuration
    logging.config.dictConfig(config)

    return _logger


