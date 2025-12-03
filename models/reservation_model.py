from database import mysql

class ReservationModel:
    @staticmethod
    def get_booked_slots(room_pk, date):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                # 방 정보 조회
                cursor.execute("SELECT building_name, room_no FROM buildings WHERE id = %s", (room_pk,))
                room_info = cursor.fetchone()

                if not room_info:
                    print(f" 방 {room_pk}에 해당하는 정보가 없습니다.")
                    return []

                building_name = room_info['building_name'] # room_info[0] (X)
                target_room_no = room_info['room_no']      # room_info[1] (X)

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
                          AND status = 1
                        """
                cursor.execute(query, (target_building_id, target_room_no, date))
                results = cursor.fetchall()

                booked_slots = [row['time_slot'] for row in results]
                print(f">>> DB에서 찾은 예약된 시간들: {booked_slots}")

                return booked_slots
        finally:
            conn.close()

    @staticmethod
    def create_reservation(member_id, room_pk, date, time_slot, people_count):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT building_name, room_no FROM buildings WHERE id = %s", (room_pk,))
                room_info = cursor.fetchone()

                if not room_info:
                    print(f"Error: Room ID {room_pk} not found.")
                    return False

                # [수정] 컬럼 이름 사용
                building_name = room_info['building_name']
                real_room_no = room_info['room_no']

                building_map = {
                    "백년관": 1, "어문학관": 2, "교양관": 3, "자연과학관": 4,
                    "인문경상관": 5, "공학관": 6, "학생회관": 7
                }

                mapped_building_id = building_map.get(building_name, 0)
                print(f">>> [DEBUG] 예약 저장: {building_name}({mapped_building_id}), 호실:{real_room_no}")

                query = """
                        INSERT INTO reservations
                        (member_id, building_id, room_no, date, time_slot, people_count, status)
                        VALUES (%s, %s, %s, %s, %s, %s, 1)
                        """
                cursor.execute(query, (member_id, mapped_building_id, real_room_no, date, time_slot, people_count))
                conn.commit()
                return True
        except Exception as e:
            print(f"Booking Error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close() # 연결 닫기

    @staticmethod
    def get_reservations_by_member(member_id):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                query = """
                        SELECT id, building_id, room_no, date, time_slot, people_count
                        FROM reservations
                        WHERE member_id = %s AND status = 1
                        ORDER BY date DESC, time_slot ASC
                        """
                cursor.execute(query, (member_id,))
                results = cursor.fetchall()

                id_to_name_map = {
                    1: "백년관", 2: "어문학관", 3: "교양관",
                    4: "자연과학관", 5: "인문경상관", 6: "공학관", 7: "학생회관"
                }

                reservations = []
                for row in results:

                    b_id = row['building_id']
                    b_name = id_to_name_map.get(b_id, "Unknown")

                    reservations.append({
                        "id": row['id'],
                        "building_name": b_name,
                        "room_no": row['room_no'],
                        "date": str(row['date']),
                        "time_slot": row['time_slot'],
                        "people_count": row['people_count']
                    })

                return reservations
        finally:
            conn.close()

    @staticmethod
    def delete_reservation(reservation_id, member_id):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                query = "DELETE FROM reservations WHERE id = %s AND member_id = %s"
                cursor.execute(query, (reservation_id, member_id))
                conn.commit()

                if cursor.rowcount > 0:
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Cancel Error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()