from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from models.member_model import MemberModel

# Blueprint 생성
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 1. 로그인 페이지 및 로직
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # API 요청 (JSON)
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # DB에서 사용자 조회
    user = MemberModel.find_by_email(email)

    # user 구조가 튜플이라고 가정 (id, email, password, name, ...)
    if user and user[2] == password:
        session['user_id'] = user[0]
        session['user_name'] = user[3] # 이름 저장
        # 로그인 성공 시 reservation 컨트롤러의 reservation_page 라우트로 이동하도록 설정
        return jsonify({"message": "Login successful", "redirect": "/reservation"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# 2. 로그아웃
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# 3. 회원가입 페이지(GET) 및 로직(POST) [수정됨]
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # GET: 페이지 렌더링
    if request.method == 'GET':
        return render_template('register.html')

    # POST: 회원가입 로직
    data = request.json

    # 프론트엔드에서 보낸 키값(fullName, mobileNumber 등) 확인
    name = data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    mobile = data.get('mobileNumber')
    student_id = data.get('studentId')

    try:
        # 1. 중복 체크
        if MemberModel.find_by_email(email):
            return jsonify({"message": "Email already exists."}), 409

        if MemberModel.find_by_student_id(student_id):
            return jsonify({"message": "Student ID already exists."}), 409

        # 2. DB 저장 (id는 DB가 알아서 만드므로 넘기지 않음)
        success = MemberModel.create_member(name, email, password, mobile, student_id)

        if success:
            # 3. 가입 성공 후 즉시 로그인 처리
            # 방금 가입한 유저 정보를 이메일로 다시 조회하여 ID와 이름을 세션에 저장
            new_user = MemberModel.find_by_email(email)
            if new_user:
                # new_user 튜플 순서: (id, email, password, name, mobile, student_id)
                session['user_id'] = new_user[0]   # id
                session['user_name'] = new_user[3] # name

            return jsonify({
                "message": "Registration successful",
                "redirect": "/reservation"
            }), 200
        else:
            return jsonify({"message": "Registration failed (DB Error)"}), 500

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({"message": f"서버 에러 발생: {str(e)}"}), 500