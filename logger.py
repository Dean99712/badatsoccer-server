import datetime
import logging

date = datetime.datetime.now().strftime('%Y-%m-%d')

logging.basicConfig(level=logging.DEBUG, filename=f'{date}-app.log')
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, filename=f'logs/{date}-app.log',)
logger = logging.getLogger(__name__)

# date = datetime.datetime.now().strftime('%Y-%m-%d')
# location = f'{date}-log.log'
#
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#
# logger = logging.getLogger(__name__)
