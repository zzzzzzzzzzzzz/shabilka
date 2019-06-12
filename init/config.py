# coding=utf-8
import logging
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

EMAIL = 'Your@email.com'
PASSWORD = 'John Wayne?'

PHANTOMJS_EXECUTABLE_PATH = os.path.join(BASE_PATH, '../drivers/phantomjs/bin/phantomjs')
LOGDIR = os.path.join(BASE_PATH, '../logs/')
PHANTOMJS_SERVICE_LOG_PATH = os.path.join(LOGDIR, 'ghostdriver.log')

CHROMEDRIVER_PATH = os.path.join(BASE_PATH, '../drivers/', 'chromedriver')

DB_HOST = '89.223.95.235'
DB_NAME = 'shabilka_db'
DB_USER = 'stuffman'
DB_USER_PASSWORD = 'stuff'

GLOBAL_LOGLEVEL = logging.DEBUG
GLOBAL_LOGGER = logging.getLogger("websim")
try:
    os.makedirs(LOGDIR)
except OSError:
    pass
hdlr = logging.FileHandler(os.path.join(LOGDIR, '{}.log'.format("websim")))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
GLOBAL_LOGGER.addHandler(hdlr)
GLOBAL_LOGGER.setLevel(GLOBAL_LOGLEVEL)


# Для указания локальных настроек типа email-а и пароля используйте файл local_config
from .local_config import *
