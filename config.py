import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'      # 본인의 MySQL 사용자명
    MYSQL_PASSWORD = '0'  # 본인의 MySQL 비밀번호
    MYSQL_DB = 'reservation_system'
    SECRET_KEY = os.urandom(24)
