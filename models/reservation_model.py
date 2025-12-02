from database import mysql

class ReservationModel:
    @staticmethod
    def get_booked_slots(room_pk, date):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT building_name, room_no FROM buildings WHERE id = %s", (room_pk,))
        room_info = cursor.fetchone()

        if not room_info:
            print(f" 방 {room_pk}에 해당하는 정보가 없습니다.")
            return []

        building_name = room_info[0]
        target_room_no = room_info[1]

        building_map = {
            "백년관": 1, "어문학과": 2, "어문학관": 2, "교양관": 3,
            "자연과학관": 4, "인문경상관": 5, "공학관": 6, "학생회관": 7
        }
        target_building_id = building_map.get(building_name, 0)

        print(f">>> 예약 조회 시도: 건물ID={target_building_id}, 호실={target_room_no}, 날짜={date}")

        query = """
                SELECT time_slot FROM reservations
                WHERE building_id = %s
                  AND room_no = %s
                  AND date = %s
                  AND status = 1 \
                """
        cursor.execute(query, (target_building_id, target_room_no, date))
        results = cursor.fetchall()
        cursor.close()
        booked_slots = [row[0] for row in results]
        print(f">>> DB에서 찾은 예약된 시간들: {booked_slots}")

        return booked_slots

    @staticmethod
    def create_reservation(member_id, room_pk, date, time_slot, people_count):
        cursor = mysql.connection.cursor()
        conn = mysql.connection

        cursor.execute("SELECT building_name, room_no FROM buildings WHERE id = %s", (room_pk,))
        room_info = cursor.fetchone()

        if not room_info:
            print(f"Error: Room ID {room_pk} not found.")
            return False

        building_name = room_info[0]
        real_room_no = room_info[1]

        # 건물 이름을 기준으로
        building_map = {
            "백년관": 1,
            "어문학관": 2,
            "교양관": 3,
            "자연과학관": 4,
            "인문경상관": 5,
            "공학관": 6,
            "학생회관": 7
        }

        mapped_building_id = building_map.get(building_name, 0)
        print(f">>> [DEBUG] 예약 저장: {building_name}({mapped_building_id}), 호실:{real_room_no}")

        query = """
                INSERT INTO reservations
                (member_id, building_id, room_no, date, time_slot, people_count, status)
                VALUES (%s, %s, %s, %s, %s, %s, 1) \
                """
        try:
            cursor.execute(query, (member_id, mapped_building_id, real_room_no, date, time_slot, people_count))
            conn.commit()
            return True
        except Exception as e:
            print(f"Booking Error: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()