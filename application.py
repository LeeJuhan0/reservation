import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template
from config import Config
from database import mysql

from controllers.auth_controller import auth_bp
from controllers.reservation_controller import reservation_bp

application = Flask(__name__, template_folder='views', static_folder='static')
app = application
application.config.from_object(Config)

mysql.init_app(application)

# 컨트롤러
application.register_blueprint(auth_bp)
application.register_blueprint(reservation_bp)

@application.route('/')
def index():
    return render_template('login.html')

@application.route('/test')
def test_connection():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE()")
        db_name = cur.fetchone()[0]
        cur.close()
        return f"<h1>성공!</h1><p>DB 연결됨: <strong>{db_name}</strong></p>"
    except Exception as e:
        return f"<h1>에러 발생!</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    application.run(debug=True, port=5000)