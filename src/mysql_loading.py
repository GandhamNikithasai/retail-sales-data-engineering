
from decimal import Decimal

import pandas as pd

from .mysql_connection import create_mysql_connection


SOURCE_SYSTEM = "retail_csv"


def get_next_key(cursor, table_name, key_column):

    # Used only with fixed internal table and column names.
    cursor.execute(
        f"SELECT COALESCE(MAX({key_column}), 0) FROM {table_name}"
    )

    return int(cursor.fetchone()[0]) + 1


def load_customer_dimension(cursor, dataframe):

    next_key = get_next_key(
        cursor, "dim_customer", "customer_key"
    )

    customer_lookup = {}

    sql = """
        INSERT INTO dim_customer (
            customer_key,
            source_system,
            customer_id,
            customer_name,
            city,
            region,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())

        ON DUPLICATE KEY UPDATE
            customer_name = VALUES(customer_name),
            city = VALUES(city),
            region = VALUES(region),
            updated_at = NOW()
    """

    for row in dataframe.itertuples(index=False):

        customer_id = str(row.customer_id)

        cursor.execute(
            """
            SELECT customer_key
            FROM dim_customer
            WHERE source_system = %s
              AND customer_id = %s
            """,
            (SOURCE_SYSTEM, customer_id)
        )

        existing = cursor.fetchone()

        if existing:
            customer_key = int(existing[0])
        else:
            customer_key = next_key
            next_key += 1

        cursor.execute(
            sql,
            (
                customer_key,
                SOURCE_SYSTEM,
                customer_id,
                str(row.customer_name),
                row.city,
                row.region
            )
        )

        # Retrieve the actual MySQL key after the upsert.
        cursor.execute(
            """
            SELECT customer_key
            FROM dim_customer
            WHERE source_system = %s
              AND customer_id = %s
            """,
            (SOURCE_SYSTEM, customer_id)
        )

        customer_lookup[customer_id] = int(
            cursor.fetchone()[0]
        )

    return customer_lookup


def load_product_dimension(cursor, dataframe):

    next_key = get_next_key(
        cursor, "dim_product", "product_key"
    )

    product_lookup = {}

    sql = """
        INSERT INTO dim_product (
            product_key,
            source_system,
            product_id,
            product_name,
            category,
            created_at,
            updated_at
        )
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())

        ON DUPLICATE KEY UPDATE
            product_name = VALUES(product_name),
            category = VALUES(category),
            updated_at = NOW()
    """

    for row in dataframe.itertuples(index=False):

        product_id = str(row.product_id)

        cursor.execute(
            """
            SELECT product_key
            FROM dim_product
            WHERE source_system = %s
              AND product_id = %s
            """,
            (SOURCE_SYSTEM, product_id)
        )

        existing = cursor.fetchone()

        if existing:
            product_key = int(existing[0])
        else:
            product_key = next_key
            next_key += 1

        cursor.execute(
            sql,
            (
                product_key,
                SOURCE_SYSTEM,
                product_id,
                str(row.product_name),
                row.category
            )
        )

        cursor.execute(
            """
            SELECT product_key
            FROM dim_product
            WHERE source_system = %s
              AND product_id = %s
            """,
            (SOURCE_SYSTEM, product_id)
        )

        product_lookup[product_id] = int(
            cursor.fetchone()[0]
        )

    return product_lookup


def load_date_dimension(cursor, dataframe):

    sql = """
        INSERT INTO dim_date (
            date_key,
            full_date,
            day_number,
            month_number,
            month_name,
            quarter_number,
            year_number,
            weekday_name,
            is_weekend
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

        ON DUPLICATE KEY UPDATE
            month_name = VALUES(month_name),
            weekday_name = VALUES(weekday_name),
            is_weekend = VALUES(is_weekend)
    """

    for row in dataframe.itertuples(index=False):

        full_date = pd.Timestamp(row.full_date).date()

        cursor.execute(
            sql,
            (
                int(row.date_key),
                full_date,
                full_date.day,
                full_date.month,
                full_date.strftime("%B"),
                (full_date.month - 1) // 3 + 1,
                full_date.year,
                full_date.strftime("%A"),
                full_date.weekday() >= 5
            )
        )


def load_sales_fact(
    cursor,
    dataframe,
    customer_lookup,
    product_lookup
):

    next_sales_key = get_next_key(
        cursor, "fact_sales", "sales_key"
    )

    sql = """
        INSERT INTO fact_sales (
            sales_key,
            source_system,
            order_item_id,
            order_id,
            customer_key,
            product_key,
            date_key,
            quantity,
            unit_price,
            gross_sales,
            discount_amount,
            net_sales,
            order_status
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )

        ON DUPLICATE KEY UPDATE
            order_id = VALUES(order_id),
            customer_key = VALUES(customer_key),
            product_key = VALUES(product_key),
            date_key = VALUES(date_key),
            quantity = VALUES(quantity),
            unit_price = VALUES(unit_price),
            gross_sales = VALUES(gross_sales),
            discount_amount = VALUES(discount_amount),
            net_sales = VALUES(net_sales),
            order_status = VALUES(order_status)
    """

    rows = []

    for row in dataframe.itertuples(index=False):

        customer_id = str(row.customer_id)
        product_id = str(row.product_id)

        if customer_id not in customer_lookup:
            raise ValueError(
                f"Customer not found in MySQL: {customer_id}"
            )

        if product_id not in product_lookup:
            raise ValueError(
                f"Product not found in MySQL: {product_id}"
            )

        quantity = int(row.quantity)

        if quantity <= 0:
            raise ValueError(
                f"Invalid quantity for item {row.order_item_id}"
            )

        unit_price = Decimal(
            str(row.unit_price)
        ).quantize(Decimal("0.01"))

        gross_sales = Decimal(
            str(row.gross_amount)
        ).quantize(Decimal("0.01"))

        discount = Decimal(
            str(row.discount_amount)
        ).quantize(Decimal("0.01"))

        net_sales = Decimal(
            str(row.net_amount)
        ).quantize(Decimal("0.01"))

        rows.append(
            (
                next_sales_key,
                SOURCE_SYSTEM,
                str(row.order_item_id),
                str(row.order_id),
                customer_lookup[customer_id],
                product_lookup[product_id],
                int(row.date_key),
                quantity,
                unit_price,
                gross_sales,
                discount,
                net_sales,
                "Completed"
            )
        )

        next_sales_key += 1

    if rows:
        cursor.executemany(sql, rows)


def load_mysql_data(transformed_data):

    connection = None

    try:

        connection = create_mysql_connection()
        cursor = connection.cursor()

        print("\nSTARTING MYSQL WAREHOUSE LOAD")

        # Step 1: Customer dimension
        customer_lookup = load_customer_dimension(
            cursor,
            transformed_data["dim_customer"]
        )

        print("Customer dimension loaded")

        # Step 2: Product dimension
        product_lookup = load_product_dimension(
            cursor,
            transformed_data["dim_product"]
        )

        print("Product dimension loaded")

        # Step 3: Date dimension
        load_date_dimension(
            cursor,
            transformed_data["dim_date"]
        )

        print("Date dimension loaded")

        # Step 4: Fact table
        load_sales_fact(
            cursor,
            transformed_data["fact_sales"],
            customer_lookup,
            product_lookup
        )

        print("Sales fact table loaded")

        # Commit everything together.
        connection.commit()

        print("\nMYSQL WAREHOUSE LOAD COMPLETED SUCCESSFULLY!")

        return True

    except Exception:

        if connection and connection.is_connected():
            connection.rollback()

        raise

    finally:

        if connection and connection.is_connected():
            connection.close()


def show_mysql_table_counts():

    connection = create_mysql_connection()

    try:

        cursor = connection.cursor()

        tables = [
            "dim_customer",
            "dim_product",
            "dim_date",
            "fact_sales"
        ]

        print("\nMYSQL WAREHOUSE SUMMARY")

        for table in tables:

            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            count = cursor.fetchone()[0]

            print(f"{table}: {count} records")

    finally:

        if connection and connection.is_connected():
            connection.close()
