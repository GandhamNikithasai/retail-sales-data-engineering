
import sqlite3
from pathlib import Path

import pytest


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "warehouse.db"


@pytest.fixture
def connection():
    assert DB_PATH.exists(), (
        f"Warehouse database does not exist: {DB_PATH}"
    )

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    yield conn

    conn.close()


def test_all_tables_exist(connection):
    cursor = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        "dim_customer",
        "dim_product",
        "dim_date",
        "dim_order",
        "fact_sales"
    }

    missing_tables = expected_tables - tables

    assert not missing_tables, (
        f"Missing warehouse tables: {missing_tables}"
    )


def test_warehouse_row_counts(connection):
    """
    Verify that all warehouse tables contain records.

    We do not use fixed expected counts because new records
    can be added through the dashboard.
    """

    tables = [
        "dim_customer",
        "dim_product",
        "dim_date",
        "dim_order",
        "fact_sales"
    ]

    actual_counts = {}

    for table in tables:
        cursor = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        actual_counts[table] = cursor.fetchone()[0]

    for table, count in actual_counts.items():
        assert count > 0, (
            f"{table} is empty. Expected at least one record."
        )


def test_fact_foreign_keys(connection):
    """
    Check whether SQLite reports any foreign-key violations.
    """

    cursor = connection.execute(
        "PRAGMA foreign_key_check"
    )

    violations = cursor.fetchall()

    assert violations == [], (
        f"Foreign-key violations found: {violations[:10]}"
    )


def test_sales_amount_calculations(connection):
    """
    Verify gross and net sales calculations.
    """

    cursor = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE ABS(
            gross_amount - (quantity * unit_price)
        ) > 0.0001
        OR ABS(
            net_amount - (gross_amount - discount_amount)
        ) > 0.0001
    """)

    incorrect_rows = cursor.fetchone()[0]

    assert incorrect_rows == 0, (
        f"{incorrect_rows} sales records have incorrect amounts."
    )


def test_fact_table_has_no_null_foreign_keys(connection):
    """
    Verify that fact table dimension keys are not NULL.
    """

    cursor = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE customer_key IS NULL
           OR product_key IS NULL
           OR date_key IS NULL
           OR order_key IS NULL
    """)

    null_rows = cursor.fetchone()[0]

    assert null_rows == 0, (
        f"{null_rows} fact records contain NULL foreign keys."
    )


def test_fact_dimension_references_exist(connection):
    """
    Verify that every fact record references existing
    customer, product, date and order dimension records.
    """

    cursor = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales f
        LEFT JOIN dim_customer c
            ON f.customer_key = c.customer_key
        LEFT JOIN dim_product p
            ON f.product_key = p.product_key
        LEFT JOIN dim_date d
            ON f.date_key = d.date_key
        LEFT JOIN dim_order o
            ON f.order_key = o.order_key
        WHERE c.customer_key IS NULL
           OR p.product_key IS NULL
           OR d.date_key IS NULL
           OR o.order_key IS NULL
    """)

    orphan_rows = cursor.fetchone()[0]

    assert orphan_rows == 0, (
        f"{orphan_rows} fact records reference missing dimension records."
    )


def test_fact_sales_has_valid_quantities_and_prices(connection):
    """
    Verify that sales records have valid quantities and prices.
    """

    cursor = connection.execute("""
        SELECT COUNT(*)
        FROM fact_sales
        WHERE quantity <= 0
           OR unit_price < 0
           OR gross_amount < 0
           OR discount_amount < 0
           OR net_amount < 0
    """)

    invalid_rows = cursor.fetchone()[0]

    assert invalid_rows == 0, (
        f"{invalid_rows} sales records contain invalid numeric values."
    )
