
import hashlib
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from .ingestion import RAW_DIR
from .mysql_connection import create_mysql_connection


PRIMARY_KEYS = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id"
}


def get_file_metadata(filename):
    """Return SHA-256 checksum and file size for a source CSV."""

    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    checksum = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            checksum.update(chunk)

    return {
        "checksum": checksum.hexdigest(),
        "file_size": file_path.stat().st_size
    }


def start_pipeline_audit(run_id, started_at):
    """Insert the initial RUNNING record."""

    connection = create_mysql_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO pipeline_runs (
                run_id,
                source_file,
                started_at,
                status
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                run_id,
                "multiple_csv_files",
                started_at,
                "RUNNING"
            )
        )

        connection.commit()
        cursor.close()

    except Exception:
        connection.rollback()
        raise

    finally:
        if connection.is_connected():
            connection.close()


def get_record_id(row, dataset_name):
    """Get a business key, falling back to the original CSV row number."""

    key = PRIMARY_KEYS[dataset_name]
    value = row.get(key)

    if pd.isna(value) or value is None:
        value = row.get("source_row_number")

    if pd.isna(value) or value is None:
        return None

    return str(value)[:100]


def clean_record(row):
    """Convert a pandas row into JSON-safe values."""

    result = {}

    for key, value in row.items():
        if value is None or pd.isna(value):
            result[key] = None
        else:
            result[key] = value

    return json.dumps(result, default=str, ensure_ascii=False)


def collect_rejections(basic_rejections, referential_rejections):
    """Combine basic and referential rejections without duplicates."""

    collected = []

    for rejection_group in (
        basic_rejections,
        referential_rejections
    ):
        for dataset_name, dataframe in rejection_group.items():

            if dataframe is None or dataframe.empty:
                continue

            source_file = f"{dataset_name}.csv"

            for _, row in dataframe.iterrows():

                record = row.to_dict()

                collected.append({
                    "source_file": source_file,
                    "source_record_id": get_record_id(
                        record, dataset_name
                    ),
                    "original_record": clean_record(record),
                    "rejection_reason": str(
                        record.get("reject_reason", "Validation failed")
                    )
                })

    # Keep one audit entry per source file and source record.
    unique_records = {}
    for record in collected:
        key = (
            record["source_file"],
            record["source_record_id"]
        )
        unique_records[key] = record

    return list(unique_records.values())


def complete_pipeline_audit(
    run_id,
    started_at,
    completed_at,
    duration_seconds,
    status,
    source_data,
    valid_data,
    basic_rejections,
    referential_rejections,
    transformed_data,
    failure_reason=None
):
    """Write ingestion history, rejected records and final run status."""

    connection = create_mysql_connection()

    try:
        cursor = connection.cursor()

        total_input = sum(
            len(df) for df in source_data.values()
        )

        total_valid = sum(
            len(df) for df in valid_data.values()
        )

        rejected_records = collect_rejections(
            basic_rejections,
            referential_rejections
        )

        total_rejected = len(rejected_records)

        duplicate_records = sum(
            1
            for record in rejected_records
            if "duplicate" in record["rejection_reason"].lower()
        )

        loaded_records = (
            len(transformed_data.get("fact_sales", []))
            if transformed_data else 0
        )

        # One ingestion history row for each source CSV.
        for dataset_name, source_df in source_data.items():

            filename = f"{dataset_name}.csv"

            metadata = get_file_metadata(filename)

            valid_count = len(
                valid_data.get(dataset_name, [])
            )

            rejected_count = max(
                len(source_df) - valid_count,
                0
            )

            ingestion_status = (
                "SUCCESS" if status == "SUCCESS" else status
            )

            cursor.execute(
                """
                INSERT INTO ingestion_history (
                    run_id,
                    source_file,
                    file_checksum,
                    file_size_bytes,
                    ingestion_started_at,
                    ingestion_completed_at,
                    input_records,
                    valid_records,
                    rejected_records,
                    status,
                    error_message
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    filename,
                    metadata["checksum"],
                    metadata["file_size"],
                    started_at,
                    completed_at,
                    len(source_df),
                    valid_count,
                    rejected_count,
                    ingestion_status,
                    failure_reason
                )
            )

        # Insert individual rejected records.
        for record in rejected_records:

            cursor.execute(
                """
                INSERT INTO rejected_records (
                    run_id,
                    source_file,
                    source_record_id,
                    original_record,
                    rejection_reason
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    record["source_file"],
                    record["source_record_id"],
                    record["original_record"],
                    record["rejection_reason"]
                )
            )

        # Update the initial pipeline_runs record.
        cursor.execute(
            """
            UPDATE pipeline_runs
            SET
                completed_at = %s,
                duration_seconds = %s,
                status = %s,
                input_records = %s,
                valid_records = %s,
                duplicate_records = %s,
                rejected_records = %s,
                loaded_records = %s,
                failure_reason = %s
            WHERE run_id = %s
            """,
            (
                completed_at,
                duration_seconds,
                status,
                total_input,
                total_valid,
                duplicate_records,
                total_rejected,
                loaded_records,
                failure_reason,
                run_id
            )
        )

        connection.commit()

        print("\nMYSQL AUDIT TRACKING COMPLETED")
        print("Input records:", total_input)
        print("Valid records:", total_valid)
        print("Rejected records:", total_rejected)
        print("Duplicate records:", duplicate_records)
        print("Loaded fact records:", loaded_records)

    except Exception:
        connection.rollback()
        raise

    finally:
        if connection.is_connected():
            connection.close()
