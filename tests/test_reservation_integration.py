import pytest
from flask import session
from database import mysql


def register_and_login(client):
    client.post('/auth/register', json={
        "fullName": "예약자2",
        "email": "booker2@test.com",
        "password": "pw",
        "mobileNumber": "010-0000-0000",
        "studentId": "20249929"
    })
    with client.session_transaction() as sess:
        user_id = sess.get('user_id')

    return user_id

def test_search_rooms(client, app):
    #방 검색 API 테스트
    # 파라미터 없이 전체 조회 혹은 필터 조회
    resp = client.get('/reservation/api/rooms?building=백년관&room_floor=1')
    assert resp.status_code == 200
    rooms = resp.json
    assert len(rooms) > 0
    assert rooms[0]['building_name'] == '백년관'
    assert rooms[0]['room_no'] == '101'
    assert rooms[0]['id'] == 1
    assert rooms[0]['capacity'] == 1
    return (rooms[0]['id'], rooms[0]['capacity'])

def test_booking_flow(client, app):
    """
    시나리오:
    1. 건물 데이터 생성
    2. 유저 회원가입/로그인
    3. 예약 가능 슬롯 확인
    4. 예약 요청
    5. 예약 확인
    6. 예약 취소
    """
    # 1. 건물 생성
    building_id = test_search_rooms(client, app)[0]
    target_date = "2024-12-25"

    # 2. 로그인
    user_id = register_and_login(client)

    # 3. 예약 가능 슬롯 확인 (아직 예약 없으므로 다 비어있어야 함)
    resp_slots = client.get(f'/reservation/api/slots?building_id={building_id}&date={target_date}')
    assert resp_slots.status_code == 200
    available_slots = resp_slots.json['available_slots']
    assert "09:00-10:00" in available_slots

    # 4. 예약 요청
    book_payload = {
        "member_id": user_id,
        "building_id": building_id,
        "date": target_date,
        "time_slot": "09:00-10:00",
        "people_count": test_search_rooms(client, app)[1]
    }
    resp_book = client.post('/reservation/api/book', json=book_payload)
    assert resp_book.status_code == 200
    assert resp_book.json['message'] == "Booking successful!"

    # 5. 예약 후 슬롯 다시 확인 (09:00-10:00이 없어야 함)
    resp_slots_2 = client.get(f'/reservation/api/slots?building_id={building_id}&date={target_date}')
    available_slots_2 = resp_slots_2.json['available_slots']
    assert "09:00-10:00" not in available_slots_2

    # 6. 내 예약 조회
    resp_my = client.get('/reservation/api/my-reservations')
    assert resp_my.status_code == 200
    my_reservations = resp_my.json
    assert len(my_reservations) == 1
    reservation_id = my_reservations[0]['id']

    # 7. 예약 취소
    cancel_payload = {"reservation_id": reservation_id}
    resp_cancel = client.post('/reservation/api/cancel', json=cancel_payload)
    assert resp_cancel.status_code == 200
    assert "cancelled successfully" in resp_cancel.json['message']

    # 8. 취소 후 슬롯 복구 확인
    resp_slots_3 = client.get(f'/reservation/api/slots?building_id={building_id}&date={target_date}')
    available_slots_3 = resp_slots_3.json['available_slots']
    assert "09:00-10:00" in available_slots_3