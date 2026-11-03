
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "warehouse.db"


def create_connection(db_path=DB_PATH):

    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables(connection):

    cursor = connection.cursor()

    # Customer dimension
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_customer (
            customer_key INTEGER PRIMARY KEY,
            customer_id TEXT NOT NULL UNIQUE,
            customer_name TEXT NOT NULL,
            city TEXT NOT NULL,
            region TEXT NOT NULL
        )
    """)

    # Product dimension
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_product (
            product_key INTEGER PRIMARY KEY,
            product_id TEXT NOT NULL UNIQUE,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL
        )
    """)

    # Date dimension
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT NOT NULL UNIQUE,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,
            quarter INTEGER NOT NULL
        )
    """)

    # Order dimension
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_order (
            order_key INTEGER PRIMARY KEY,
            order_id TEXT NOT NULL UNIQUE,
            order_status TEXT NOT NULL,
            payment_method TEXT NOT NULL
        )
    """)

    # Sales fact table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_sales (
            sales_key INTEGER PRIMARY KEY,
            order_item_id TEXT NOT NULL UNIQUE,
            order_id TEXT NOT NULL,

            customer_key INTEGER NOT NULL,
            product_key INTEGER NOT NULL,
            date_key INTEGER NOT NULL,
            order_key INTEGER NOT NULL,

            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            gross_amount REAL NOT NULL,
            discount_amount REAL NOT NULL,
            net_amount REAL NOT NULL,

            FOREIGN KEY (customer_key)
                REFERENCES dim_customer(customer_key),

            FOREIGN KEY (product_key)
                REFERENCES dim_product(product_key),

            FOREIGN KEY (date_key)
                REFERENCES dim_date(date_key),

            FOREIGN KEY (order_key)
                REFERENCES dim_order(order_key)
        )
    """)

    # Indexes for analytical queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_customer
        ON fact_sales(customer_key)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_product
        ON fact_sales(product_key)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_date
        ON fact_sales(date_key)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_order
        ON fact_sales(order_key)
    """)

    connection.commit()


def insert_dataframe(connection, table_name, dataframe):

    columns = list(dataframe.columns)

    column_names = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))

    query = f"""
        INSERT INTO {table_name} ({column_names})
        VALUES ({placeholders})
    """

    rows = []

    for row in dataframe.itertuples(index=False, name=None):

        converted_row = []

        for value in row:

            if hasattr(value, "item"):
                value = value.item()

            if hasattr(value, "isoformat"):
                value = value.isoformat()

            converted_row.append(value)

        rows.append(tuple(converted_row))

    connection.executemany(query, rows)


def load_data(transformed_data, db_path=DB_PATH):

    connection = create_connection(db_path)

    try:

        create_tables(connection)

        # Full refresh: remove old facts before dimensions.
        connection.execute("DELETE FROM fact_sales")
        connection.execute("DELETE FROM dim_order")
        connection.execute("DELETE FROM dim_date")
        connection.execute("DELETE FROM dim_product")
        connection.execute("DELETE FROM dim_customer")

        # Insert dimensions first.
        insert_dataframe(
            connection,
            "dim_customer",
            transformed_data["dim_customer"]
        )

        insert_dataframe(
            connection,
            "dim_product",
            transformed_data["dim_product"]
        )

        insert_dataframe(
            connection,
            "dim_date",
            transformed_data["dim_date"]
        )

        insert_dataframe(
            connection,
            "dim_order",
            transformed_data["dim_order"]
        )

        # SQLite schema does not require the original business IDs.
# Keep customer_id and product_id in transformed_data
# because the MySQL loader needs them.

        sqlite_fact_sales = transformed_data["fact_sales"].drop(
            columns=["customer_id", "product_id"],
            errors="ignore"
        )

        insert_dataframe(
            connection,
            "fact_sales",
            sqlite_fact_sales
        )

        # Commit all changes together.
        connection.commit()

        print("\nDATABASE LOAD COMPLETED SUCCESSFULLY!")

        return True

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def show_table_counts(db_path=DB_PATH):

    connection = create_connection(db_path)

    try:

        tables = [
            "dim_customer",
            "dim_product",
            "dim_date",
            "dim_order",
            "fact_sales"
        ]

        print("\nDATABASE TABLE SUMMARY")

        for table in tables:

            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count} records")

    finally:

        connection.close()


if __name__ == "__main__":

    from .ingestion import ingest_data
    from .validation import validate_all
    from .transformation import transform_data

    print("STARTING ETL PIPELINE")

    source_data = ingest_data()

    valid_data = validate_all(source_data)

    transformed_data = transform_data(valid_data)

    load_data(transformed_data)

    show_table_counts()

    print("\nETL LOADING STAGE COMPLETED!")
