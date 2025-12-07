import os

class Config:
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '0')
    MYSQL_DB = os.environ.get('DB_NAME', 'reservation_system')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'local_fixed_key_1234')