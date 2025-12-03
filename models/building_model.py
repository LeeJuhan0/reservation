from database import mysql

class BuildingModel:
    @staticmethod
    def get_rooms_by_filter(building_name=None, room_floor=None):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM buildings WHERE 1=1"
                params = []

                print(f">>> [DEBUG] 검색 요청 받음 - 건물: '{building_name}', 층: '{room_floor}'")

                # 건물 이름 필터
                if building_name and building_name != "Select Building":
                    query += " AND building_name = %s"
                    params.append(building_name)

                # 층수 필터
                if room_floor and str(room_floor).strip() != "" and "Select" not in str(room_floor):
                    query += " AND room_floor = %s"
                    params.append(room_floor)

                # 정렬 (방 번호를 숫자로 변환하여 정렬)
                query += " ORDER BY building_name, CAST(room_no AS UNSIGNED), room_floor"

                print(f">>> [DEBUG] 실행할 쿼리: {query}")
                print(f">>> [DEBUG] 파라미터: {params}")

                cursor.execute(query, tuple(params))
                results = cursor.fetchall()

                rooms = []
                if results:
                    for row in results:
                        rooms.append({
                            "id": row['id'],
                            "building_name": row['building_name'],
                            "room_no": row['room_no'],
                            "room_type": row['room_type'],
                            "room_floor": row['room_floor'],
                            "desk_type": row['desk_type'],
                            "capacity": row['capacity'],
                            "availability": row['availability'],
                            "remark": row['remark']
                        })
                return rooms
        finally:
            conn.close()

    @staticmethod
    def get_room_no_by_id(building_id):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                query = "SELECT room_no FROM buildings WHERE id = %s"
                cursor.execute(query, (building_id,))
                result = cursor.fetchone()

                return result['room_no'] if result else None
        finally:
            conn.close()