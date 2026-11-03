
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUARANTINE_DIR = BASE_DIR / "data" / "quarantine"


def validate_referential_integrity(data, return_rejected=False):
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        name: df.copy()
        for name, df in data.items()
    }

    rejected_results = {}

    # Check customer references in orders.
    valid_customer_ids = set(
        data["customers"]["customer_id"].dropna()
    )

    invalid_orders_mask = ~data["orders"]["customer_id"].isin(
        valid_customer_ids
    )

    invalid_orders = data["orders"][invalid_orders_mask].copy()
    valid_orders = data["orders"][~invalid_orders_mask].copy()

    if not invalid_orders.empty:
        invalid_orders["reject_reason"] = (
            "customer_id does not exist in customers"
        )

        invalid_orders.to_csv(
            QUARANTINE_DIR / "referential_rejected_orders.csv",
            index=False
        )

    rejected_results["orders"] = invalid_orders
    data["orders"] = valid_orders

    # Check order and product references in order items.
    valid_order_ids = set(
        data["orders"]["order_id"].dropna()
    )

    valid_product_ids = set(
        data["products"]["product_id"].dropna()
    )

    valid_order_items_mask = (
        data["order_items"]["order_id"].isin(valid_order_ids)
        &
        data["order_items"]["product_id"].isin(valid_product_ids)
    )

    invalid_order_items = data["order_items"][
        ~valid_order_items_mask
    ].copy()

    valid_order_items = data["order_items"][
        valid_order_items_mask
    ].copy()

    if not invalid_order_items.empty:
        reasons = []

        for _, row in invalid_order_items.iterrows():
            row_reasons = []

            if row["order_id"] not in valid_order_ids:
                row_reasons.append("Invalid order_id")

            if row["product_id"] not in valid_product_ids:
                row_reasons.append("Invalid product_id")

            reasons.append("; ".join(row_reasons))

        invalid_order_items["reject_reason"] = reasons

        invalid_order_items.to_csv(
            QUARANTINE_DIR / "referential_rejected_order_items.csv",
            index=False
        )

    rejected_results["order_items"] = invalid_order_items
    data["order_items"] = valid_order_items

    print("\nREFERENTIAL INTEGRITY SUMMARY")
    print(f"Orders rejected: {len(invalid_orders)}")
    print(f"Order items rejected: {len(invalid_order_items)}")
    print(f"Valid orders remaining: {len(data['orders'])}")
    print(f"Valid order items remaining: {len(data['order_items'])}")

    if return_rejected:
        return data, rejected_results

    # Preserve the old return behavior for the existing pipeline.
    return data
