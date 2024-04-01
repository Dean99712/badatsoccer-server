# import os
#
# from dotenv import load_dotenv
#
# load_dotenv()
#
#
# class Config:
#     driver = os.getenv('DRIVER')
#     server = os.getenv('SERVER')
#     port = os.getenv('PORT')
#     database = os.getenv('DATABASE')
#     uid = os.getenv('UID')
#     password = os.getenv('PASSWORD')


class Config:
    driver = "{ODBC Driver 18 for SQL Server}"
    server = "tcp:flask-server-database.database.windows.net"
    port = 1433
    database = "bad_at_soccer"
    uid = "dbadmin"
    password = "Admin123"
