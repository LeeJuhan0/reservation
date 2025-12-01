from flask import Flask, render_template
from config import Config
from database import mysql # [중요] 여기서 불러오기

# 컨트롤러 블루프린트 임포트
from controllers.auth_controller import auth_bp
from controllers.reservation_controller import reservation_bp

app = Flask(__name__, template_folder='views', static_folder='static')
app.config.from_object(Config)

# [중요] MySQL 객체에 앱 연결하기
mysql.init_app(app)

# 컨트롤러 등록
app.register_blueprint(auth_bp)
app.register_blueprint(reservation_bp)

@app.route('/')
def index():
    return render_template('login.html')

# [진단용] 이제는 extensions를 안 쓰지만 연결 테스트는 가능
@app.route('/test')
def test_connection():
    try:
        # mysql 객체를 직접 사용해서 테스트
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE()")
        db_name = cur.fetchone()[0]
        cur.close()
        return f"<h1>성공!</h1><p>DB 연결됨: <strong>{db_name}</strong></p>"
    except Exception as e:
        return f"<h1>에러 발생!</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)