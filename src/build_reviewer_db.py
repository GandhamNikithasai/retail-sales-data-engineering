
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .ingestion import ingest_data
from .validation import validate_all
from .referential_validation import validate_referential_integrity
from .transformation import transform_data
from .loading import load_data, DB_PATH


BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "reports"
REPORT_PATH = REPORT_DIR / "reviewer_summary.json"


def get_sqlite_counts():
    """Return row counts from the local SQLite warehouse."""

    tables = [
        "dim_customer",
        "dim_product",
        "dim_date",
        "dim_order",
        "fact_sales",
    ]

    connection = sqlite3.connect(DB_PATH)

    try:
        counts = {}

        for table in tables:
            counts[table] = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

        return counts

    finally:
        connection.close()


def build_reviewer_database():
    """Build the local reviewer database without MySQL."""

    print("=" * 55)
    print("BUILDING REVIEWER DATABASE")
    print("SQLite-only mode: MySQL is not used")
    print("=" * 55)

    try:
        # Step 1: Read the original CSV files.
        print("\nSTEP 1: DATA INGESTION")
        source_data = ingest_data()

        source_counts = {
            name: len(df)
            for name, df in source_data.items()
        }

        print("Source records:", source_counts)

        # Step 2: Validate source data.
        print("\nSTEP 2: DATA VALIDATION")
        valid_data, basic_rejections = validate_all(
            source_data,
            return_rejected=True,
        )

        # Step 3: Validate relationships between datasets.
        print("\nSTEP 3: REFERENTIAL INTEGRITY")
        valid_data, referential_rejections = (
            validate_referential_integrity(
                valid_data,
                return_rejected=True,
            )
        )

        valid_counts = {
            name: len(df)
            for name, df in valid_data.items()
        }

        # Step 4: Transform the validated data.
        print("\nSTEP 4: DATA TRANSFORMATION")
        transformed_data = transform_data(valid_data)

        transformed_counts = {
            name: len(df)
            for name, df in transformed_data.items()
        }

        # Step 5: Load only into SQLite.
        print("\nSTEP 5: SQLITE WAREHOUSE LOADING")
        load_data(transformed_data)

        # Step 6: Verify the database.
        print("\nSTEP 6: DATABASE VERIFICATION")
        loaded_counts = get_sqlite_counts()

        if not loaded_counts["fact_sales"]:
            raise RuntimeError(
                "The SQLite warehouse contains no sales records."
            )

        # Step 7: Save reviewer report.
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

        report = {
            "mode": "REVIEWER_MODE",
            "status": "SUCCESS",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "database": str(DB_PATH.relative_to(BASE_DIR)),
            "mysql_required": False,
            "source_rows": source_counts,
            "valid_rows": valid_counts,
            "transformed_rows": transformed_counts,
            "loaded_sqlite_rows": loaded_counts,
            "basic_rejections": {
                name: len(df)
                for name, df in basic_rejections.items()
            },
            "referential_rejections": {
                name: len(df)
                for name, df in referential_rejections.items()
            },
        }

        with open(REPORT_PATH, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        print("\nREVIEWER DATABASE CREATED SUCCESSFULLY")
        print("Database:", DB_PATH)
        print("Report:", REPORT_PATH)
        print("SQLite records:", loaded_counts)

        return report

    except Exception as error:
        print("\nREVIEWER DATABASE BUILD FAILED")
        print("Error:", error)
        raise


if __name__ == "__main__":
    build_reviewer_database()
