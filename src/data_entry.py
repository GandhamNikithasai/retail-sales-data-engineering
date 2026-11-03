
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

CSV_FILES = {
    "customers": RAW_DIR / "customers.csv",
    "products": RAW_DIR / "products.csv",
    "orders": RAW_DIR / "orders.csv",
    "order_items": RAW_DIR / "order_items.csv"
}

REQUIRED_COLUMNS = {
    "customers": [
        "customer_id", "customer_name", "city", "region"
    ],
    "products": [
        "product_id", "product_name", "category", "unit_price"
    ],
    "orders": [
        "order_id", "customer_id", "order_date",
        "order_status", "payment_method"
    ],
    "order_items": [
        "order_item_id", "order_id", "product_id",
        "quantity", "unit_price", "discount_amount"
    ]
}


def read_csv(dataset):
    """Read a source CSV without changing its original structure."""

    path = CSV_FILES[dataset]

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    return pd.read_csv(path, dtype=str).fillna("")


def clean_text(value, field):
    value = str(value).strip()

    if not value:
        raise ValueError(f"{field} is required.")

    return value


def check_unique_id(dataset, id_column, record_id):
    dataframe = read_csv(dataset)

    if record_id in dataframe[id_column].astype(str).values:
        raise ValueError(
            f"{id_column} '{record_id}' already exists."
        )


def append_record(dataset, record):
    """Validate columns and append one record to its source CSV."""

    if dataset not in CSV_FILES:
        raise ValueError(f"Unknown dataset: {dataset}")

    expected_columns = REQUIRED_COLUMNS[dataset]

    if set(record.keys()) != set(expected_columns):
        raise ValueError(
            f"Incorrect fields supplied for {dataset}."
        )

    path = CSV_FILES[dataset]
    dataframe = read_csv(dataset)

    # Confirm the existing CSV has the expected structure.
    if list(dataframe.columns) != expected_columns:
        raise ValueError(
            f"Unexpected CSV structure in {path.name}."
        )

    new_row = pd.DataFrame(
        [[str(record[column]).strip() for column in expected_columns]],
        columns=expected_columns
    )

    new_row.to_csv(
        path,
        mode="a",
        header=False,
        index=False,
        encoding="utf-8"
    )

    return True


def add_customer(customer_id, customer_name, city, region):
    customer_id = clean_text(customer_id, "Customer ID")
    customer_name = clean_text(customer_name, "Customer name")
    city = clean_text(city, "City")
    region = clean_text(region, "Region")

    check_unique_id("customers", "customer_id", customer_id)

    append_record("customers", {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "city": city,
        "region": region
    })

    return "Customer saved successfully."


def add_product(product_id, product_name, category, unit_price):
    product_id = clean_text(product_id, "Product ID")
    product_name = clean_text(product_name, "Product name")
    category = clean_text(category, "Category")

    try:
        price = float(unit_price)
    except (TypeError, ValueError):
        raise ValueError("Unit price must be a valid number.")

    if price < 0:
        raise ValueError("Unit price cannot be negative.")

    check_unique_id("products", "product_id", product_id)

    append_record("products", {
        "product_id": product_id,
        "product_name": product_name,
        "category": category,
        "unit_price": price
    })

    return "Product saved successfully."


def add_order(
    order_id,
    customer_id,
    order_date,
    order_status,
    payment_method
):
    order_id = clean_text(order_id, "Order ID")
    customer_id = clean_text(customer_id, "Customer ID")
    order_status = clean_text(order_status, "Order status")
    payment_method = clean_text(payment_method, "Payment method")

    check_unique_id("orders", "order_id", order_id)

    customers = read_csv("customers")

    if customer_id not in customers["customer_id"].values:
        raise ValueError("Selected customer does not exist.")

    parsed_date = pd.to_datetime(
        order_date,
        errors="coerce"
    )

    if pd.isna(parsed_date):
        raise ValueError("Please enter a valid order date.")

    allowed_statuses = ["Completed", "Pending", "Cancelled"]

    if order_status not in allowed_statuses:
        raise ValueError("Invalid order status.")

    append_record("orders", {
        "order_id": order_id,
        "customer_id": customer_id,
        "order_date": parsed_date.strftime("%Y-%m-%d"),
        "order_status": order_status,
        "payment_method": payment_method
    })

    return "Order saved successfully."


def add_order_item(
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_amount
):
    order_item_id = clean_text(order_item_id, "Order item ID")
    order_id = clean_text(order_id, "Order ID")
    product_id = clean_text(product_id, "Product ID")

    check_unique_id(
        "order_items", "order_item_id", order_item_id
    )

    orders = read_csv("orders")
    products = read_csv("products")

    if order_id not in orders["order_id"].values:
        raise ValueError("Selected order does not exist.")

    if product_id not in products["product_id"].values:
        raise ValueError("Selected product does not exist.")

    try:
        quantity = int(quantity)
        unit_price = float(unit_price)
        discount_amount = float(discount_amount)
    except (TypeError, ValueError):
        raise ValueError(
            "Quantity, unit price and discount must be valid numbers."
        )

    if quantity <= 0:
        raise ValueError("Quantity must be a positive integer.")

    if unit_price < 0:
        raise ValueError("Unit price cannot be negative.")

    if discount_amount < 0:
        raise ValueError("Discount cannot be negative.")

    gross_amount = quantity * unit_price

    if discount_amount > gross_amount:
        raise ValueError("Discount cannot exceed gross amount.")

    append_record("order_items", {
        "order_item_id": order_item_id,
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_amount": discount_amount
    })

    return "Order item saved successfully."
