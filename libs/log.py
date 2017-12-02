# -*- coding: utf-8 -*-
'''
@summary: logger for the whole project
@author: zhouqiang
'''
import os
import logging
from libs.misc import mkdirs
from inner_conf import LOG_DIR
import tornado.log
from tornado.log import access_log, app_log, gen_log

mkdirs(LOG_DIR)
app_handler = logging.FileHandler(LOG_DIR + "/app.log")
access_handler = logging.FileHandler(LOG_DIR + "/access.log")
gen_handler = logging.FileHandler(LOG_DIR + "/gen.log")

formatter = tornado.log.LogFormatter(
    fmt='%(color)s[ %(asctime)s ] %(end_color)s %(message)s',
    datefmt='%y/%m/%d %H:%M:%S')

app_handler.setFormatter(formatter)
access_handler.setFormatter(formatter)
gen_handler.setFormatter(formatter)

app_log.addHandler(app_handler)
access_log.addHandler(access_handler)
gen_log.addHandler(gen_handler)

access_log.setLevel(logging.INFO)
app_log.setLevel(logging.INFO)
gen_log.setLevel(logging.INFO)