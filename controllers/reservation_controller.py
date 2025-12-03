from flask import Blueprint, render_template, request, jsonify, session
from models.building_model import BuildingModel
from models.reservation_model import ReservationModel

reservation_bp = Blueprint('reservation', __name__, url_prefix='/reservation')

# 예약 메인 페이지 렌더링
@reservation_bp.route('/', methods=['GET'])
def reservation_page():
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('reservation.html')

#  API 영역

#  방 검색 API
@reservation_bp.route('/api/rooms', methods=['GET'])
def search_rooms():
    building = request.args.get('building')

    room_floor = request.args.get('room_floor')

    print(f">>> [CONTROLLER] 건물: {building}, 층: {room_floor}") # 확인용 로그

    rooms = BuildingModel.get_rooms_by_filter(building, room_floor)
    return jsonify(rooms), 200

# 예약 가능한 슬롯 API
@reservation_bp.route('/api/slots', methods=['GET'])
def get_available_slots():
    building_id = request.args.get('building_id')
    date = request.args.get('date')

    if not building_id or not date:
        return jsonify({"message": "Missing parameters"}), 400

    all_slots = [
        "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
        "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00"
    ]

    booked_slots = ReservationModel.get_booked_slots(building_id, date)

    available_slots = [slot for slot in all_slots if slot not in booked_slots]

    return jsonify({"available_slots": available_slots}), 200

# 예약하기(Booking) API
@reservation_bp.route('/api/book', methods=['POST'])
def book_room():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    building_id = data.get('building_id')
    date = data.get('date')
    time_slot = data.get('time_slot')
    people_count = data.get('people_count')
    member_id = session['user_id']

    if not all([building_id, date, time_slot, people_count]):
        return jsonify({"message": "Missing data"}), 400

    success = ReservationModel.create_reservation(member_id, building_id, date, time_slot, people_count)

    if success:
        return jsonify({"message": "Booking successful!"}), 200
    else:
        return jsonify({"message": "Booking failed."}), 500

@reservation_bp.route('/mypage', methods=['GET'])
def my_page():
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('mypage.html')
# 예약가져오기 api
@reservation_bp.route('/api/my-reservations', methods=['GET'])
def get_my_reservations():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user_id = session['user_id']
    reservations = ReservationModel.get_reservations_by_member(user_id)
    return jsonify(reservations), 200

# 예약취소api
@reservation_bp.route('/api/cancel', methods=['POST'])
def cancel_reservation():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    reservation_id = data.get('reservation_id')
    user_id = session['user_id']

    if not reservation_id:
        return jsonify({"message": "Missing reservation ID"}), 400

    success = ReservationModel.delete_reservation(reservation_id, user_id)

    if success:
        return jsonify({"message": "Reservation cancelled successfully."}), 200
    else:
        return jsonify({"message": "Failed to cancel. It might be already deleted."}), 400