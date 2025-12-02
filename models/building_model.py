from database import mysql

class BuildingModel:
    @staticmethod
    def get_rooms_by_filter(building_name=None, room_floor=None):
        cursor = mysql.connection.cursor()

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

        query += " ORDER BY building_name, CAST(room_no AS UNSIGNED), room_floor"

        print(f">>> [DEBUG] 실행할 쿼리: {query}")
        print(f">>> [DEBUG] 파라미터: {params}")

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()

        rooms = []
        if results:
            for row in results:
                rooms.append({
                    "id": row[0],
                    "building_name": row[1],
                    "room_no": row[2],
                    "room_type": row[3],
                    "room_floor": row[4],
                    "desk_type": row[5],
                    "capacity": row[6],
                    "availability": row[7],
                    "remark": row[8]
                })
        return rooms

    @staticmethod
    def get_room_no_by_id(building_id):
        cursor = mysql.connection.cursor()
        query = "SELECT room_no FROM buildings WHERE id = %s"
        cursor.execute(query, (building_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None