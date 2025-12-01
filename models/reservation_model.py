from flask import current_app
from database import mysql

def get_cursor():
    return current_app.extensions['mysql'].connection.cursor()

def get_conn():
    return current_app.extensions['mysql'].connection

class ReservationModel:
    @staticmethod
    def get_reserved_slots(building_id, date):
        """
        특정 날짜, 특정 방에 이미 예약된 시간 슬롯 목록을 반환
        """
        cursor = mysql.connection.cursor()
        # 취소된 예약('Cancelled')은 제외하고 조회
        query = """
                SELECT time_slot
                FROM reservations
                WHERE building_id = %s AND reservations.date = %s AND status != 0 \
                """
        try:
            cursor.execute(query, (building_id, date))
            rows = cursor.fetchall()
            # rows는 [('10:00',), ('14:30',)] 형태이므로 리스트로 변환
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Error fetching reserved slots: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def is_slot_available(building_id, date, time_slot):
        """
        해당 슬롯이 비어있는지 확인 (True: 예약 가능, False: 이미 예약됨)
        """
        cursor = mysql.connection.cursor()
        query = """
                SELECT COUNT(*)
                FROM reservations
                WHERE building_id = %s AND reservations.date = %s AND time_slot = %s AND status != 0 \
                """
        try:
            cursor.execute(query, (building_id, date, time_slot))
            count = cursor.fetchone()[0]
            return count == 0
        except Exception as e:
            print(f"Error checking slot availability: {e}")
            return False
        finally:
            cursor.close()

    @staticmethod
    def create_reservation(member_id, building_id, date, time_slot, people_count, status='Reserved'):
        cursor = mysql.connection.cursor()
        conn = mysql.connection
        query = """
                INSERT INTO reservations
                (member_id, building_id, date, time_slot, people_count, status )
                VALUES (%s, %s, %s, %s, %s, %s) \
                """
        try:
            cursor.execute(query, (member_id, building_id, date, time_slot, people_count, status))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating reservation: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()