from database import mysql

class MemberModel:
    @staticmethod
    def find_by_email(email):
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM members WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        return result

    @staticmethod
    def find_by_student_id(student_id):
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM members WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    @staticmethod
    def create_member(name, email, password, mobile, student_id):
        cursor = mysql.connection.cursor()
        conn = mysql.connection

        query = """
                INSERT INTO members (name, email, password, mobile_number, student_id)
                VALUES (%s, %s, %s, %s, %s) \
                """
        try:
            cursor.execute(query, (name, email, password, mobile, student_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"SQL Error: {e}")
            conn.rollback()
            raise e
        finally:
            cursor.close()