import pytest
from flask import session

def test_register_and_login_flow(client):
    """
    시나리오:
    1. 회원가입 요청
    2. DB에 저장되었는지 확인 (로그인 시도)
    3. 내 정보 확인 (/auth/me)
    """
    # 1. 회원가입
    user_data = {
        "fullName": "테스트유저",
        "email": "test@example.com",
        "password": "password123",
        "mobileNumber": "010-1234-5678",
        "studentId": "20240001"
    }
    resp_reg = client.post('/auth/register', json=user_data)
    assert resp_reg.status_code == 200
    assert resp_reg.json['message'] == "Registration successful"

    # 세션 확인 (자동 로그인)
    with client.session_transaction() as sess:
        assert sess['user_name'] == "테스트유저"

    # 2. 로그아웃
    client.get('/auth/logout')

    # 3. 로그인
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    resp_login = client.post('/auth/login', json=login_data)
    assert resp_login.status_code == 200
    assert resp_login.json['message'] == "Login successful"

    # 4. 내 정보 확인
    resp_me = client.get('/auth/me')
    assert resp_me.status_code == 200
    assert resp_me.json['name'] == "테스트유저"

def test_register_duplicate_email(client):
    """이메일 중복 가입 방지 테스트"""
    user_data = {
        "fullName": "유저1",
        "email": "dup@example.com",
        "password": "pw",
        "mobileNumber": "010-1111-1111",
        "studentId": "20240002"
    }
    # 첫 번째 가입
    client.post('/auth/register', json=user_data)

    # 두 번째 가입 (이메일 중복)
    user_data['studentId'] = "20240003" # 학번은 다르게
    resp = client.post('/auth/register', json=user_data)

    assert resp.status_code == 409
    assert "Email already exists" in resp.json['message']