import pandas as pd


def transform_data(data):

    customers = data["customers"].copy()
    products = data["products"].copy()
    orders = data["orders"].copy()
    order_items = data["order_items"].copy()

    # Clean business IDs.
    for df, columns in [
        (customers, ["customer_id"]),
        (products, ["product_id"]),
        (orders, ["order_id", "customer_id"]),
        (order_items, ["order_item_id", "order_id", "product_id"])
    ]:
        for column in columns:
            df[column] = df[column].astype(str).str.strip()

    # Convert numeric and date fields.
    products["unit_price"] = pd.to_numeric(
        products["unit_price"], errors="coerce"
    )

    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce"
    )

    order_items["quantity"] = pd.to_numeric(
        order_items["quantity"], errors="coerce"
    )

    order_items["unit_price"] = pd.to_numeric(
        order_items["unit_price"], errors="coerce"
    )

    order_items["discount_amount"] = pd.to_numeric(
        order_items["discount_amount"], errors="coerce"
    ).fillna(0)

    # Remove invalid and duplicate master records.
    customers = customers.dropna(
        subset=["customer_id", "customer_name"]
    ).drop_duplicates("customer_id")

    products = products.dropna(
        subset=["product_id", "product_name", "unit_price"]
    ).drop_duplicates("product_id")

    orders = orders.dropna(
        subset=["order_id", "customer_id", "order_date"]
    ).drop_duplicates("order_id")

    # Keep only orders with existing customers.
    orders = orders[
        orders["customer_id"].isin(customers["customer_id"])
    ].copy()

    # Create customer dimension.
    dim_customer = customers[
        ["customer_id", "customer_name", "city", "region"]
    ].copy()

    dim_customer = dim_customer.sort_values(
        "customer_id"
    ).reset_index(drop=True)

    dim_customer.insert(
        0, "customer_key", range(1, len(dim_customer) + 1)
    )

    # Create product dimension.
    dim_product = products[
        ["product_id", "product_name", "category", "unit_price"]
    ].copy()

    dim_product = dim_product.sort_values(
        "product_id"
    ).reset_index(drop=True)

    dim_product.insert(
        0, "product_key", range(1, len(dim_product) + 1)
    )

    # Create order dimension.
    dim_order = orders[
        ["order_id", "order_status", "payment_method"]
    ].copy()

    dim_order = dim_order.sort_values(
        "order_id"
    ).reset_index(drop=True)

    dim_order.insert(
        0, "order_key", range(1, len(dim_order) + 1)
    )

    # Create a dynamic date dimension.
    if orders.empty:
        raise ValueError("No valid orders available for transformation.")

    min_date = orders["order_date"].min().normalize()
    max_date = orders["order_date"].max().normalize()

    dates = pd.date_range(min_date, max_date, freq="D")

    dim_date = pd.DataFrame({"full_date": dates})

    dim_date["date_key"] = (
        dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    )

    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["quarter"] = dim_date["full_date"].dt.quarter

    dim_date["full_date"] = dim_date["full_date"].dt.date

    dim_date = dim_date[
        ["date_key", "full_date", "year", "month", "day", "quarter"]
    ]

    # Create lookup dictionaries.
    customer_lookup = dict(
        zip(dim_customer["customer_id"], dim_customer["customer_key"])
    )

    product_lookup = dict(
        zip(dim_product["product_id"], dim_product["product_key"])
    )

    order_lookup = dict(
        zip(dim_order["order_id"], dim_order["order_key"])
    )

    date_lookup = dict(
        zip(
            pd.to_datetime(dim_date["full_date"]).dt.date,
            dim_date["date_key"]
        )
    )

    # Only completed orders contribute to sales.
    completed_orders = orders[
        orders["order_status"].astype(str).str.strip().str.lower()
        == "completed"
    ].copy()

    # Attach order information to order items.
    fact_sales = order_items.merge(
        completed_orders[
            ["order_id", "customer_id", "order_date"]
        ],
        on="order_id",
        how="inner"
    )

    # Keep valid products and sales values.
    fact_sales = fact_sales[
        fact_sales["product_id"].isin(product_lookup)
    ].copy()

    fact_sales = fact_sales.dropna(
        subset=["quantity", "unit_price"]
    )

    fact_sales = fact_sales[
        (fact_sales["quantity"] > 0)
        & (fact_sales["unit_price"] >= 0)
        & (fact_sales["discount_amount"] >= 0)
    ].copy()

    # Calculate sales amounts.
    fact_sales["gross_amount"] = (
        fact_sales["quantity"] * fact_sales["unit_price"]
    )

    fact_sales["net_amount"] = (
        fact_sales["gross_amount"] - fact_sales["discount_amount"]
    )

    fact_sales = fact_sales[
        fact_sales["net_amount"] >= 0
    ].copy()

    # Map surrogate keys.
    fact_sales["customer_key"] = (
        fact_sales["customer_id"].map(customer_lookup)
    )

    fact_sales["product_key"] = (
        fact_sales["product_id"].map(product_lookup)
    )

    fact_sales["order_key"] = (
        fact_sales["order_id"].map(order_lookup)
    )

    fact_sales["date_key"] = (
        fact_sales["order_date"].dt.date.map(date_lookup)
    )

    fact_sales = fact_sales.dropna(
        subset=[
            "customer_key",
            "product_key",
            "order_key",
            "date_key"
        ]
    ).copy()

    # Assign fact table surrogate keys.
    fact_sales = fact_sales.sort_values(
        "order_item_id"
    ).reset_index(drop=True)

    fact_sales.insert(
        0, "sales_key", range(1, len(fact_sales) + 1)
    )

    for column in [
        "sales_key",
        "customer_key",
        "product_key",
        "order_key",
        "date_key"
    ]:
        fact_sales[column] = fact_sales[column].astype("int64")

    fact_sales["quantity"] = fact_sales["quantity"].astype("int64")

    # Keep the columns required by both existing loaders.
    fact_sales = fact_sales[
        [
            "sales_key",
            "order_item_id",
            "order_id",
            "customer_id",
            "product_id",
            "customer_key",
            "product_key",
            "date_key",
            "order_key",
            "quantity",
            "unit_price",
            "gross_amount",
            "discount_amount",
            "net_amount"
        ]
    ].copy()

    return {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_date": dim_date,
        "dim_order": dim_order,
        "fact_sales": fact_sales
    }