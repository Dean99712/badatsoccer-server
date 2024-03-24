import datetime
import logging

date = datetime.datetime.now().strftime('%Y-%m-%d')
location = f'./logs/{date}-log.log'

logging.basicConfig(filename=location, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# log_file_path = f'./logs/{date}-log.log'
# file_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024 * 100, backupCount=10)
# file_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
