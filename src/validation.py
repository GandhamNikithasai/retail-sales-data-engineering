
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUARANTINE_DIR = BASE_DIR / "data" / "quarantine"

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


def validate_required_columns(name, df):
    missing = set(REQUIRED_COLUMNS[name]) - set(df.columns)

    if missing:
        raise ValueError(
            f"{name}: Missing required columns: {sorted(missing)}"
        )


def validate_dataset(name, df):
    validate_required_columns(name, df)

    df = df.copy()

    for column in REQUIRED_COLUMNS[name]:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    reject_reasons = [[] for _ in range(len(df))]

    def reject(mask, reason):
        for index, invalid in enumerate(mask.fillna(False)):
            if invalid:
                reject_reasons[index].append(reason)

    # Required fields
    for column in REQUIRED_COLUMNS[name]:
        reject(
            df[column].isna(),
            f"Missing value: {column}"
        )

    # Duplicate primary-key checks
    primary_keys = {
        "customers": "customer_id",
        "products": "product_id",
        "orders": "order_id",
        "order_items": "order_item_id"
    }

    key = primary_keys[name]

    reject(
        df[key].notna() & df[key].duplicated(keep="first"),
        f"Duplicate {key}"
    )

    # Product validation
    if name == "products":
        price = pd.to_numeric(df["unit_price"], errors="coerce")

        reject(
            price.isna() & df["unit_price"].notna(),
            "Invalid unit_price"
        )

        reject(
            price.notna() & (price < 0),
            "unit_price cannot be negative"
        )

    # Order validation
    if name == "orders":
        dates = pd.to_datetime(
            df["order_date"],
            format="%Y-%m-%d",
            errors="coerce"
        )

        reject(
            dates.isna() & df["order_date"].notna(),
            "Invalid order_date; expected YYYY-MM-DD"
        )

        reject(
            ~df["order_status"].isin(
                ["Completed", "Pending", "Cancelled"]
            ) & df["order_status"].notna(),
            "Invalid order_status"
        )

    # Order-item validation
    if name == "order_items":
        quantity = pd.to_numeric(
            df["quantity"], errors="coerce"
        )
        price = pd.to_numeric(
            df["unit_price"], errors="coerce"
        )
        discount = pd.to_numeric(
            df["discount_amount"], errors="coerce"
        )

        reject(
            quantity.isna() & df["quantity"].notna(),
            "Invalid quantity"
        )

        reject(
            quantity.notna() & (
                (quantity <= 0) | (quantity % 1 != 0)
            ),
            "quantity must be a positive integer"
        )

        reject(
            price.isna() & df["unit_price"].notna(),
            "Invalid unit_price"
        )

        reject(
            price.notna() & (price < 0),
            "unit_price cannot be negative"
        )

        reject(
            discount.isna() & df["discount_amount"].notna(),
            "Invalid discount_amount"
        )

        reject(
            discount.notna() & (discount < 0),
            "discount_amount cannot be negative"
        )

        gross = quantity * price

        reject(
            discount.notna() & gross.notna() & (discount > gross),
            "Discount cannot exceed gross amount"
        )

    df["reject_reason"] = [
        "; ".join(reasons) if reasons else ""
        for reasons in reject_reasons
    ]

    rejected = df[df["reject_reason"] != ""].copy()
    valid = df[df["reject_reason"] == ""].copy()

    return valid, rejected


def validate_all(data, return_rejected=False):
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    valid_results = {}
    rejected_results = {}

    for name, df in data.items():
        valid, rejected = validate_dataset(name, df)

        valid_results[name] = valid
        rejected_results[name] = rejected

        if not rejected.empty:
            rejected.to_csv(
                QUARANTINE_DIR / f"rejected_{name}.csv",
                index=False
            )

        print(
            f"VALIDATION: {name} | "
            f"Valid: {len(valid)} | "
            f"Rejected: {len(rejected)}"
        )

    if return_rejected:
        return valid_results, rejected_results

    # Preserve the old return behavior for the existing pipeline.
    return valid_results
