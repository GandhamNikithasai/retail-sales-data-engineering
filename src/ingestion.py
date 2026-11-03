
import argparse
import time
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def read_source_file(filename, raw_dir=RAW_DIR):

    raw_dir = Path(raw_dir)
    file_path = raw_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {file_path}"
        )

    start_time = time.perf_counter()

    df = pd.read_csv(file_path, dtype=str)

    # Preserve original CSV row number.
    df.insert(
        0,
        "source_row_number",
        range(2, len(df) + 2)
    )

    elapsed = time.perf_counter() - start_time
    memory_mb = (
        df.memory_usage(deep=True).sum() / (1024 * 1024)
    )

    print(
        f"INGESTED: {filename} | "
        f"Records: {len(df):,} | "
        f"Time: {elapsed:.2f} seconds | "
        f"Memory: {memory_mb:.2f} MB"
    )

    return df


def ingest_data(raw_dir=None):

    if raw_dir is None:
        raw_dir = RAW_DIR

    customers = read_source_file(
        "customers.csv", raw_dir
    )

    products = read_source_file(
        "products.csv", raw_dir
    )

    orders = read_source_file(
        "orders.csv", raw_dir
    )

    order_items = read_source_file(
        "order_items.csv", raw_dir
    )

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Retail CSV ingestion"
    )

    parser.add_argument(
        "--input-dir",
        type=str,
        default=str(RAW_DIR),
        help="Directory containing source CSV files"
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)

    print("=" * 60)
    print("RETAIL DATA INGESTION")
    print("=" * 60)
    print(f"Input directory: {input_dir}")

    start_time = time.perf_counter()

    data = ingest_data(input_dir)

    total_time = time.perf_counter() - start_time

    print("\nINGESTION SUMMARY")

    total_records = 0
    total_memory = 0

    for name, df in data.items():
        records = len(df)
        memory_mb = (
            df.memory_usage(deep=True).sum()
            / (1024 * 1024)
        )

        total_records += records
        total_memory += memory_mb

        print(
            f"{name}: {records:,} records | "
            f"{memory_mb:.2f} MB"
        )

    print("-" * 60)
    print(f"Total records: {total_records:,}")
    print(f"Total DataFrame memory: {total_memory:.2f} MB")
    print(f"Total ingestion time: {total_time:.2f} seconds")

    if total_time > 0:
        throughput = total_records / total_time
        print(f"Ingestion throughput: {throughput:,.0f} rows/second")

    print("\nINGESTION COMPLETED SUCCESSFULLY!")
