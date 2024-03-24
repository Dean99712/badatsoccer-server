import datetime
import logging

date = datetime.datetime.now().strftime('%Y-%m-%d')
location = f'./logs/{date}-log.log'

logging.basicConfig(filename=location, level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def log_message(request, status_code):
    time = datetime.datetime.now().strftime('%d/%b/%Y %H:%M:%S')
    return f'{time} - logging - {logging.INFO} - - [{date}] "{request.method} {request.path} HTTP/1.1" {status_code} -'


logger = logging.getLogger(__name__)
