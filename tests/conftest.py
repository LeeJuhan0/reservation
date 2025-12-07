import pytest
from flask import Flask
# 실제 모듈 import (경로에 주의하세요)
from controllers.auth_controller import auth_bp
from controllers.reservation_controller import reservation_bp
from database import mysql

# --- DB 접속 정보 설정 (테스트용 DB 사용 권장) ---
# 주의: 로컬 환경에 맞는 계정과 비밀번호, 그리고 '테스트용 DB 이름'을 입력하세요.
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '0224'        # 본인 비밀번호
DB_NAME = 'reservation_system'     # 테스트 전용 DB 권장

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__, template_folder='../views')
    app.secret_key = 'test_secret_key'
    app.testing = True

    # DB 설정 주입
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

