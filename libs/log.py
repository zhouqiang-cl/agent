# -*- coding: utf-8 -*-
'''
@summary: logger for the whole project
@author: zhouqiang
'''
import os
import logging
from inner_conf import LOG_DIR


def get_logger():
    '''
    @summary: init logger
    @result: return a logger object
    '''
    logger_ = logging.getLogger("agent")
    formatter = logging.Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] %(message)s', '%Y-%m-%d %H:%M:%S',)
    handler = logging.FileHandler(LOG_DIR + '/agent.log')
    handler.setFormatter(formatter)
    logger_.addHandler(handler)
    logger_.setLevel(logging.DEBUG)
    return logger_

if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)
logger = get_logger()
