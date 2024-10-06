import logging
import os
from datetime import date
from logging.handlers import RotatingFileHandler

LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

cur_date = date.today()
LOG_NAME = f'app-log-{cur_date}.log'

LOG_FILE = os.path.join(LOGS_DIR, LOG_NAME)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=20)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)


def log_message(request, status_code):
    if status_code == 200:
        return logger.info(f'"{request.method} {request.path}  HTTP/1.1" {status_code}')
    if status_code == 400:
        return logger.error(f'"{request.method} {request.path}  HTTP/1.1" {status_code}')


logger.addHandler(file_handler)

#
# logger = logging.getLogger(__name__)
