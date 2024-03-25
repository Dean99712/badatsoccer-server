import datetime
import logging
import os
from logging.handlers import RotatingFileHandler

LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)
formatted_datetime = datetime.datetime.now().strftime('%Y-%m-%d')

LOG_PATH = f'{formatted_datetime}-app.log'

LOG_FILE = os.path.join(LOGS_DIR, LOG_PATH)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=20)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, filename=f'logs/{date}-app.log',)
logger.addHandler(file_handler)

#
# logger = logging.getLogger(__name__)
