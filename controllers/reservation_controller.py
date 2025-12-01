from flask import Blueprint, request, jsonify, render_template, session
from models.building_model import BuildingModel
from models.reservation_model import ReservationModel

reservation_bp = Blueprint('reservation', __name__, url_prefix='/reservation')

# 1. 예약 페이지 렌더링
@reservation_bp.route('/', methods=['GET'])
def reservation_page():
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('reservation.html')


# 2. 방 목록 조회 API
@reservation_bp.route('/api/rooms', methods=['GET'])
def get_rooms():
    """
    Query Params:
    - building: 건물 이름 (VARCHAR)
    - room_no: 호실 번호 (VARCHAR '1'~'14')
    """
    building_name = request.args.get('building', '')
    room_no = request.args.get('room_no', '')

    # DB에서 필터링된 방 목록 가져오기
    # BuildingModel.get_rooms_by_filter는 building_name과 room_no를 WHERE 조건으로 사용
    rooms = BuildingModel.get_rooms_by_filter(building_name, room_no)

    # 상태 코드 매핑
    status_map = {0: 'Vacant', 1: 'Reserved', 2: 'Dirty', 3: 'Occupied'}

    processed_rooms = []
    for room in rooms:
        # DB 컬럼명과 JS가 기대하는 키 이름 매핑
        r_data = {
            'id': room['id'],                  # building_id (PK)
            'room_no': room['room_no'],        # VARCHAR
            'building': room['building_name'], # DB 컬럼명이 building_name이라고 가정
            'type': room.get('room_type', 'Study'), # DB 컬럼명에 맞게 수정 필요
            'floor': room.get('floor', 'N/A'),
            'desk_type': room.get('desk_type', 'Standard'),
            'capacity': room['people_count'],  # 수용 인원
            'status': status_map.get(room.get('availability', 0), 'Unknown'),
            'remarks': room.get('remarks', '')
        }
        processed_rooms.append(r_data)

    return jsonify(processed_rooms)


# 3. 예약 가능 슬롯 조회 API
@reservation_bp.route('/api/slots', methods=['GET'])
def find_slots():
    """
    Query Params:
    - room_id: 방 ID (PK)
    - date: 날짜 (YYYY-MM-DD)
    - people: 인원 수
    """
    room_id = request.args.get('room_id')
    date = request.args.get('date')
    people_count = request.args.get('people', type=int)

    if not room_id or not date:
        return jsonify({"message": "Missing parameters"}), 400

    # 3-1. 방 정보 조회 및 인원 초과 검증
    room_info = BuildingModel.get_room_by_id(room_id)
    if not room_info:
        return jsonify({"message": "Room not found"}), 404

    if people_count and people_count > room_info['people_count']:
        return jsonify({"message": f"Exceeds capacity ({room_info['people_count']})"}), 400

    # 3-2. 전체 시간 슬롯 생성 (9시~17시, 1시간 단위, 12시 제외)
    # 요청사항: 09:00, 10:00, 11:00, 13:00, 14:00, 15:00, 16:00
    all_slots = [
        "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00", "16:00"
    ]
    # (참고: 17:00까지 '사용 가능'하다면 16:00 타임이 마지막 슬롯이 됨.
    # 만약 17:00 시작 슬롯도 포함하려면 리스트에 "17:00" 추가)

    # 3-3. 예약된 슬롯 조회 (Reservations 테이블)
    # 해당 날짜, 해당 room_id에 대해 예약된 time_slot 목록을 가져옴
    reserved_slots = ReservationModel.get_reserved_slots(room_id, date)

    # 3-4. 예약 가능한 슬롯 필터링 (차집합)
    available_slots = [slot for slot in all_slots if slot not in reserved_slots]

    return jsonify(available_slots)


# 4. 예약 생성 API
@reservation_bp.route('/api/book', methods=['POST'])
def create_booking():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json

    # 데이터 추출
    room_id = data.get('room_id')
    date = data.get('date')         # date 타입
    time_slot = data.get('time_slot') # varchar
    people = data.get('people')     # int

    if not all([room_id, date, time_slot, people]):
        return jsonify({"message": "Missing booking information"}), 400

    # 4-1. 중복 예약 재확인 (동시성 제어)
    if not ReservationModel.is_slot_available(room_id, date, time_slot):
        return jsonify({"message": "This slot is already booked."}), 409

    # 4-2. 예약 생성
    success = ReservationModel.create_reservation(
        member_id=session['user_id'],
        building_id=room_id,
        date=date,
        time_slot=time_slot,
        people_count=people,
        status='Reserved'
    )

    if success:
        return jsonify({"message": "Booking successful"}), 200
    else:
        return jsonify({"message": "Database error"}), 500