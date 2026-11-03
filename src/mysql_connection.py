import os
import mysql.connector
from mysql.connector import Error


def create_mysql_connection():
    """
    MySQL connection is disabled by default.

    Enable it only when running the ETL pipeline yourself.
    Reviewers do not need MySQL credentials.
    """

    enabled = os.getenv("ENABLE_MYSQL_ETL", "false").lower()

    if enabled != "true":
        raise RuntimeError(
            "MySQL is disabled. Reviewer Mode uses local prepared data "
            "and does not require database credentials."
        )

    required_variables = [
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
    ]

    missing = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing:
        raise RuntimeError(
            "Missing MySQL configuration: " + ", ".join(missing)
        )

    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )


def test_mysql_connection():
    connection = None
    cursor = None

    try:
        connection = create_mysql_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT VERSION(), DATABASE(), CURRENT_USER()"
        )

        result = cursor.fetchone()

        print("MYSQL CONNECTION SUCCESSFUL!")
        print("MySQL Version:", result[0])
        print("Database:", result[1])
        print("MySQL User:", result[2])

        return True

    except (Error, RuntimeError) as error:
        print("MYSQL CONNECTION FAILED!")
        print("Reason:", error)
        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    test_mysql_connection()