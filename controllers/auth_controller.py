from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from models.member_model import MemberModel

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 로그인 페이지
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # API 요청
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = MemberModel.find_by_email(email)

    if user and user['password'] == password:
        session['user_id'] = user['id']
        session['user_name'] = user['name'] # 이름 저장
        return jsonify({"message": "Login successful", "redirect": "/reservation"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# 로그아웃
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# 회원가입 페이지
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.json

    name = data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    mobile = data.get('mobileNumber')
    student_id = data.get('studentId')

    try:
        # 중복 체크
        if MemberModel.find_by_email(email):
            return jsonify({"message": "Email already exists."}), 409

        if MemberModel.find_by_student_id(student_id):
            return jsonify({"message": "Student ID already exists."}), 409

        # DB 저장
        success = MemberModel.create_member(name, email, password, mobile, student_id)

        if success:
            #  가입 성공 후 즉시 로그인
            new_user = MemberModel.find_by_email(email)
            if new_user:
                session['user_id'] = new_user['id']   # id
                session['user_name'] = new_user['name']  # name

            return jsonify({
                "message": "Registration successful",
                "redirect": "/reservation"
            }), 200
        else:
            return jsonify({"message": "Registration failed (DB Error)"}), 500

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({"message": f"서버 에러 발생: {str(e)}"}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({"message": "Not logged in", "name": "Guest"}), 401

    return jsonify({
        "user_id": session['user_id'],
        "name": session.get('user_name', 'User')
    }), 200