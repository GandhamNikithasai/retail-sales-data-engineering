
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "warehouse.db"
SQL_PATH = BASE_DIR / "reports" / "analytics.sql"


def run_analytics():

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_PATH}")

    with open(SQL_PATH, "r", encoding="utf-8") as file:
        sql_content = file.read()

    queries = [
        query.strip()
        for query in sql_content.split(";")
        if query.strip()
    ]

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        for index, query in enumerate(queries, start=1):

            if not query.lstrip().upper().startswith("SELECT"):
                continue

            cursor.execute(query)

            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()

            print(f"\n{'=' * 50}")
            print(f"ANALYTICS QUERY {index}")
            print("=" * 50)

            print(" | ".join(columns))

            for row in rows:
                print(" | ".join(str(value) for value in row))

    finally:
        connection.close()


if __name__ == "__main__":
    run_analytics()
