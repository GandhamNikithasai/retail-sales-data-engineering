
import csv
import random
import argparse
from pathlib import Path
from datetime import date, timedelta

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"


def generate_data(
    number_of_orders,
    start_date,
    end_date,
    seed=42,
    output_dir=None
):
    random.seed(seed)

    # Use the original directory unless another is specified
    target_dir = Path(output_dir) if output_dir else RAW_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    date_difference = (end_date - start_date).days

    # 1. Generate customers
    cities = {
        "Hyderabad": "South",
        "Delhi": "North",
        "Mumbai": "West",
        "Chennai": "South",
        "Kolkata": "East"
    }

    customers = []

    for i in range(1, 101):
        city = random.choice(list(cities.keys()))

        customers.append({
            "customer_id": f"C{i:04d}",
            "customer_name": f"Customer_{i}",
            "city": city,
            "region": cities[city]
        })

    # 2. Generate products
    categories = [
        "Electronics",
        "Clothing",
        "Furniture",
        "Accessories"
    ]

    products = []

    for i in range(1, 31):
        products.append({
            "product_id": f"P{i:04d}",
            "product_name": f"Product_{i}",
            "category": random.choice(categories),
            "unit_price": round(random.uniform(100, 50000), 2)
        })

    # 3. Generate orders
    orders = []

    for i in range(1, number_of_orders + 1):
        random_days = random.randint(0, date_difference)
        order_date = start_date + timedelta(days=random_days)

        orders.append({
            "order_id": f"O{i:06d}",
            "customer_id": random.choice(customers)["customer_id"],
            "order_date": order_date.isoformat(),
            "order_status": random.choices(
                ["Completed", "Pending", "Cancelled"],
                weights=[75, 15, 10]
            )[0],
            "payment_method": random.choice(
                ["UPI", "Credit Card", "Debit Card", "Cash"]
            )
        })

    # 4. Generate order items
    order_items = []
    item_id = 1

    for order in orders:
        selected_products = random.sample(
            products,
            random.randint(1, 3)
        )

        for product in selected_products:
            quantity = random.randint(1, 5)
            price = product["unit_price"]
            gross = quantity * price

            discount = round(
                gross * random.choice([0, 0.05, 0.10]),
                2
            )

            order_items.append({
                "order_item_id": f"OI{item_id:08d}",
                "order_id": order["order_id"],
                "product_id": product["product_id"],
                "quantity": quantity,
                "unit_price": price,
                "discount_amount": discount
            })

            item_id += 1

    # 5. Save CSV files
    datasets = {
        "customers.csv": customers,
        "products.csv": products,
        "orders.csv": orders,
        "order_items.csv": order_items
    }

    fieldnames = {
        "customers.csv": [
            "customer_id", "customer_name", "city", "region"
        ],
        "products.csv": [
            "product_id", "product_name", "category", "unit_price"
        ],
        "orders.csv": [
            "order_id", "customer_id", "order_date",
            "order_status", "payment_method"
        ],
        "order_items.csv": [
            "order_item_id", "order_id", "product_id",
            "quantity", "unit_price", "discount_amount"
        ]
    }

    for filename, rows in datasets.items():
        with open(
            target_dir / filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames[filename]
            )

            writer.writeheader()
            writer.writerows(rows)

        print(f"{filename}: {len(rows)} records generated")

    print("\nDATA GENERATION COMPLETED SUCCESSFULLY!")
    print(f"Output directory: {target_dir}")
    print(f"Start date: {start_date}")
    print(f"End date:   {end_date}")
    print(f"Orders:     {number_of_orders}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate retail sales data"
    )

    parser.add_argument(
        "--orders",
        type=int,
        default=500
    )

    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        default=date(2025, 1, 1)
    )

    parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        default=date(2025, 12, 31)
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional separate output directory"
    )

    args = parser.parse_args()

    if args.orders < 0:
        parser.error("--orders must be non-negative")

    if args.start_date > args.end_date:
        parser.error("--start-date cannot be after --end-date")

    generate_data(
        number_of_orders=args.orders,
        start_date=args.start_date,
        end_date=args.end_date,
        seed=args.seed,
        output_dir=args.output_dir
    )
