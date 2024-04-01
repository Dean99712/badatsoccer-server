import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    driver = os.getenv('DRIVER')
    server = os.getenv('SERVER')
    port = os.getenv('PORT')
    database = os.getenv('DATABASE')
    uid = os.getenv('UID')
    password = os.getenv('PASSWORD')
