# -*- coding: utf-8 -*-
'''
@summary: logger for the whole project
@author: zhouqiang
'''
import os
import logging
from libs.misc import mkdirs
from inner_conf import LOG_DIR
from tornado.log import access_log, app_log, gen_log


app_handler = logging.FileHandler(LOG_DIR + "/app.log")
access_handler = logging.FileHandler(LOG_DIR + "/access.log")
gen_handler = logging.FileHandler(LOG_DIR + "/gen.log")

app_log.addHandler(app_handler)
access_log.addHandler(access_handler)
gen_log.addHandler(gen_handler)

access_log.setLevel(logging.INFO)
app_log.setLevel(logging.INFO)
gen_log.setLevel(logging.INFO)