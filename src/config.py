# coding=utf-8
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

EMAIL = 'Your@email.com'
PASSWORD = 'John Wayne?'

PHANTOMJS_EXECUTABLE_PATH = 'phantomjs/bin/phantomjs'
PHANTOMJS_SERVICE_LOG_PATH = '../logs/ghostdriver.log'

CHROMEDRIVER_PATH = os.path.join(BASE_PATH, 'chromedriver')

DB_HOST = 'localhost'
DB_NAME = 'shabilka_db'
DB_USER = 'stuffman'
DB_USER_PASSWORD = 'stuff'


# Для указания локальных настроек типа email-а и пароля используйте файл local_config
from local_config import *
