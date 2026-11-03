import time
from pathlib import Path

from .ingestion import ingest_data
from .transformation import transform_data


BASE_DIR = Path(__file__).resolve().parent.parent

TEST_RAW_DIR = (
    BASE_DIR / "data" / "performance_test" / "raw"
)


def memory_usage(data):

    total_memory = 0

    for name, df in data.items():

        memory_mb = (
            df.memory_usage(deep=True).sum()
            / (1024 * 1024)
        )

        total_memory += memory_mb

        print(
            f"{name}: {len(df):,} records | "
            f"{memory_mb:.2f} MB"
        )

    return total_memory


def run_performance_test():

    print("=" * 60)
    print("RETAIL ETL PERFORMANCE TEST")
    print("=" * 60)

    if not TEST_RAW_DIR.exists():
        raise FileNotFoundError(
            f"Performance data not found: {TEST_RAW_DIR}"
        )

    total_start = time.perf_counter()

    # Step 1: Ingestion
    ingestion_start = time.perf_counter()

    source_data = ingest_data(raw_dir=TEST_RAW_DIR)

    ingestion_time = (
        time.perf_counter() - ingestion_start
    )

    print("\nSOURCE DATA SUMMARY")

    source_memory = memory_usage(source_data)

    # Step 2: Transformation
    transformation_start = time.perf_counter()

    transformed_data = transform_data(source_data)

    transformation_time = (
        time.perf_counter() - transformation_start
    )

    print("\nTRANSFORMED DATA SUMMARY")

    transformed_memory = memory_usage(transformed_data)

    # Step 3: Data quality checks
    fact_sales = transformed_data["fact_sales"]

    required_keys = [
        "customer_key",
        "product_key",
        "date_key",
        "order_key"
    ]

    missing_keys = (
        fact_sales[required_keys]
        .isnull()
        .any(axis=1)
        .sum()
    )

    invalid_sales = (
        (fact_sales["quantity"] <= 0)
        | (fact_sales["unit_price"] < 0)
        | (fact_sales["gross_amount"] < 0)
        | (fact_sales["discount_amount"] < 0)
        | (fact_sales["net_amount"] < 0)
        | (
            fact_sales["gross_amount"]
            != fact_sales["quantity"] * fact_sales["unit_price"]
        )
        | (
            fact_sales["net_amount"]
            != fact_sales["gross_amount"]
            - fact_sales["discount_amount"]
        )
    ).sum()

    duplicate_facts = fact_sales[
        "order_item_id"
    ].duplicated().sum()

    total_time = time.perf_counter() - total_start

    total_source_records = sum(
        len(df) for df in source_data.values()
    )

    print("\n" + "=" * 60)
    print("PERFORMANCE TEST RESULTS")
    print("=" * 60)

    print(f"Source records: {total_source_records:,}")
    print(f"Fact sales records: {len(fact_sales):,}")

    print(f"Ingestion time: {ingestion_time:.2f} seconds")
    print(
        f"Transformation time: "
        f"{transformation_time:.2f} seconds"
    )
    print(f"Total execution time: {total_time:.2f} seconds")

    print(f"Source memory: {source_memory:.2f} MB")
    print(f"Transformed memory: {transformed_memory:.2f} MB")

    if transformation_time > 0:
        throughput = (
            total_source_records / transformation_time
        )

        print(
            f"Transformation throughput: "
            f"{throughput:,.0f} rows/second"
        )

    print(f"Missing foreign keys: {missing_keys}")
    print(f"Invalid sales records: {invalid_sales}")
    print(f"Duplicate fact records: {duplicate_facts}")

    print("\nTRANSFORMED TABLE COUNTS")

    for name, df in transformed_data.items():
        print(f"{name}: {len(df):,}")

    print("\n" + "=" * 60)

    if (
        missing_keys == 0
        and invalid_sales == 0
        and duplicate_facts == 0
    ):
        print("PERFORMANCE TEST PASSED!")
    else:
        print("PERFORMANCE TEST FAILED: CHECK DATA QUALITY")

    print("=" * 60)


if __name__ == "__main__":
    run_performance_test()