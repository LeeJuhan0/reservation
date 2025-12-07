import pytest
from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.reservation_controller import reservation_bp
from database import mysql

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '0'        
DB_NAME = 'reservation_system'     

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__, template_folder='../views')
    app.secret_key = 'test_secret_key'
    app.testing = True

    app.config['MYSQL_HOST'] = DB_HOST
    app.config['MYSQL_USER'] = DB_USER
    app.config['MYSQL_PASSWORD'] = DB_PASSWORD
    app.config['MYSQL_DB'] = DB_NAME
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(reservation_bp)

    return app

@pytest.fixture
def client(app):
    return app.test_client()

