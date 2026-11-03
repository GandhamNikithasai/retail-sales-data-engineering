
import os
import mysql.connector
from mysql.connector import Error


def create_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv(
            "MYSQL_DATABASE",
            "yottaflex_retail_dw"
        )
    )


def test_mysql_connection():
    connection = None

    try:
        connection = create_mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT VERSION(), DATABASE(), CURRENT_USER()
        """)

        result = cursor.fetchone()

        print("\nMYSQL CONNECTION SUCCESSFUL!")
        print("MySQL Version:", result[0])
        print("Database:", result[1])
        print("MySQL User:", result[2])

        cursor.close()
        return True

    except Error as error:
        print("\nMYSQL CONNECTION FAILED!")
        print("Error:", error)
        return False

    finally:
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    test_mysql_connection()
