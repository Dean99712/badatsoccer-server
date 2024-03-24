from ftplib import FTP

ftp_server = 'ftps://waws-prod-blu-437.ftp.azurewebsites.windows.net/site/wwwroot'
ftp_user = 'python-flask-webapp-t\$python-flask-webapp-t'
ftp_password = 'JgGiYtWoD7dqg8aPWDledpNnu2q0f1c8F1MCA5d24iGmgPsJlZ93ghmBncnd'


def ftp_connect():
    ftp = FTP(ftp_server)
    ftp.login(user=ftp_user, passwd=ftp_password)
