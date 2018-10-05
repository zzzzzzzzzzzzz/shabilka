# coding=utf-8
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

EMAIL = 'Your@email.com'
PASSWORD = 'John Wayne?'

PHANTOMJS_EXECUTABLE_PATH = 'phantomjs/bin/phantomjs'
PHANTOMJS_SERVICE_LOG_PATH = '../logs/ghostdriver.log'

CHROMEDRIVER_PATH = os.path.join(BASE_PATH, 'chromedriver')

from local_config import *
