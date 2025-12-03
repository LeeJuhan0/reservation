from database import mysql

class MemberModel:
    @staticmethod
    def find_by_email(email):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM members WHERE email = %s"
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return result
        finally:
            conn.close()

    @staticmethod
    def find_by_student_id(student_id):
        conn = mysql.connection  #
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM members WHERE student_id = %s"
                cursor.execute(query, (student_id,))
                result = cursor.fetchone()
                return result
        finally:
            conn.close()

    @staticmethod
    def create_member(name, email, password, mobile, student_id):
        conn = mysql.connection
        try:
            with conn.cursor() as cursor:
                query = """
                        INSERT INTO members (name, email, password, mobile_number, student_id)
                        VALUES (%s, %s, %s, %s, %s) \
                        """
                cursor.execute(query, (name, email, password, mobile, student_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"회원가입 에러: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()