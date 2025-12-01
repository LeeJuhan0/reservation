from flask import current_app
from database import mysql

def get_cursor():
    return current_app.extensions['mysql'].connection.cursor()

def get_conn():
    return current_app.extensions['mysql'].connection

class BuildingModel:
    @staticmethod
    def get_rooms_by_filter(building_name=None, room_no=None):
        cursor = mysql.connection.cursor()

        # 기본 쿼리
        query = "SELECT * FROM buildings WHERE 1=1"
        params = []

        # 건물 필터
        if building_name and building_name.lower() != 'all':
            query += " AND building_name = %s"
            params.append(building_name)

        # 호실 번호 필터
        if room_no:
            query += " AND room_no = %s"
            params.append(room_no)

        try:
            cursor.execute(query, tuple(params))

            # 딕셔너리 형태로 변환
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        except Exception as e:
            print(f"Error fetching rooms: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def get_room_by_id(room_id):
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM buildings WHERE id = %s"

        try:
            cursor.execute(query, (room_id,))
            row = cursor.fetchone()

            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            print(f"Error fetching room by id: {e}")
            return None
        finally:
            cursor.close()

    @staticmethod
    def update_availability(room_id, status_code):
        cursor = mysql.connection.cursor()
        conn = mysql.connection
        try:
            cursor.execute("UPDATE buildings SET availability = %s WHERE id = %s", (status_code, room_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating availability: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()