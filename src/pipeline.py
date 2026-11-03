
import json
import logging
import sqlite3
import sys
import time
import uuid

from .audit import (
    start_pipeline_audit,
    complete_pipeline_audit
)

from datetime import datetime, timezone
from pathlib import Path

from .ingestion import ingest_data
from .validation import validate_all
from .referential_validation import validate_referential_integrity
from .transformation import transform_data

from .loading import load_data, DB_PATH
from .mysql_loading import load_mysql_data
from .mysql_connection import create_mysql_connection


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

LOG_FILE = LOG_DIR / "pipeline.log"
REPORT_FILE = REPORT_DIR / "run_summary.json"


# --------------------------------------------------
# LOGGING CONFIGURATION
# --------------------------------------------------

def setup_logging():

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )


# --------------------------------------------------
# SQLITE DATABASE ROW COUNTS
# --------------------------------------------------

def get_database_counts():

    if not Path(DB_PATH).exists():
        return {}

    tables = [
        "dim_customer",
        "dim_product",
        "dim_date",
        "dim_order",
        "fact_sales"
    ]

    counts = {}

    connection = sqlite3.connect(DB_PATH)

    try:

        cursor = connection.cursor()

        for table in tables:

            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            counts[table] = cursor.fetchone()[0]

    finally:
        connection.close()

    return counts


# --------------------------------------------------
# MYSQL DATABASE ROW COUNTS
# --------------------------------------------------

def get_mysql_database_counts():

    tables = [
        "dim_customer",
        "dim_product",
        "dim_date",
        "fact_sales"
    ]

    counts = {}

    connection = create_mysql_connection()

    try:

        cursor = connection.cursor()

        for table in tables:

            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            counts[table] = cursor.fetchone()[0]

        cursor.close()

    finally:

        if connection and connection.is_connected():
            connection.close()

    return counts


# --------------------------------------------------
# SAVE PIPELINE REPORT
# --------------------------------------------------

def save_report(report):

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(REPORT_FILE, "w", encoding="utf-8") as file:

        json.dump(
            report,
            file,
            indent=4
        )


# --------------------------------------------------
# MAIN ETL PIPELINE
# --------------------------------------------------

def run_pipeline():
    source_data = {}
    valid_data = {}
    transformed_data = {}
    basic_rejections = {}
    referential_rejections = {}
    audit_started = False

    # MySQL DATETIME columns use a timezone-naive datetime.
    audit_started_at = datetime.now()


    setup_logging()

    logger = logging.getLogger(__name__)

    run_id = str(uuid.uuid4())

    start_time = datetime.now(timezone.utc)

    start_clock = time.perf_counter()

    report = {
        "run_id": run_id,
        "status": "RUNNING",
        "start_time": start_time.isoformat(),
        "end_time": None,
        "duration_seconds": 0,
        "source_rows": {},
        "valid_rows": {},
        "rejected_rows": {},
        "transformed_rows": {},
        "loaded_rows": {
            "mysql": {},
            "sqlite": {}
        },
        "error": None
    }

    source_data = {}
    valid_data = {}
    transformed_data = {}

    logger.info("=" * 60)
    logger.info("RETAIL SALES ETL PIPELINE STARTED")
    logger.info("Run ID: %s", run_id)

    try:

        # Create the audit record before processing starts.
        start_pipeline_audit(run_id, audit_started_at)
        audit_started = True

        logger.info("MYSQL AUDIT RUN CREATED")

        # ------------------------------------------
        # STEP 1: DATA INGESTION
        # ------------------------------------------

        logger.info("STEP 1: DATA INGESTION")

        source_data = ingest_data()

        report["source_rows"] = {
            name: len(df)
            for name, df in source_data.items()
        }

        logger.info("INGESTION COMPLETED")


        # ------------------------------------------
        # STEP 2: BASIC DATA VALIDATION
        # ------------------------------------------

        logger.info("STEP 2: DATA VALIDATION")

        valid_data, basic_rejections = validate_all(
            source_data,
            return_rejected=True
        )

        logger.info("BASIC VALIDATION COMPLETED")


        # ------------------------------------------
        # STEP 3: REFERENTIAL INTEGRITY
        # ------------------------------------------

        logger.info("STEP 3: REFERENTIAL INTEGRITY VALIDATION")

        valid_data, referential_rejections = (
            validate_referential_integrity(
                valid_data,
                return_rejected=True
            )
        )

        logger.info("REFERENTIAL VALIDATION COMPLETED")


        # ------------------------------------------
        # STEP 4: VALIDATION SUMMARY
        # ------------------------------------------

        report["valid_rows"] = {
            name: len(df)
            for name, df in valid_data.items()
        }

        report["rejected_rows"] = {
            name: (
                report["source_rows"].get(name, 0)
                - report["valid_rows"].get(name, 0)
            )
            for name in report["source_rows"]
        }


        # ------------------------------------------
        # STEP 5: DATA TRANSFORMATION
        # ------------------------------------------

        logger.info("STEP 4: DATA TRANSFORMATION")

        transformed_data = transform_data(valid_data)

        report["transformed_rows"] = {
            name: len(df)
            for name, df in transformed_data.items()
        }

        logger.info("TRANSFORMATION COMPLETED")


        # ------------------------------------------
        # STEP 6: LOAD INTO MYSQL
        # ------------------------------------------

        logger.info("STEP 5: LOADING DATA INTO MYSQL")

        load_mysql_data(transformed_data)

        logger.info("MYSQL LOADING COMPLETED")


        # ------------------------------------------
        # STEP 7: LOAD INTO SQLITE BACKUP
        # ------------------------------------------

        logger.info("STEP 6: LOADING DATA INTO SQLITE BACKUP")

        load_data(transformed_data)

        logger.info("SQLITE BACKUP LOADING COMPLETED")


        # ------------------------------------------
        # STEP 8: DATABASE VERIFICATION
        # ------------------------------------------

        logger.info("STEP 7: DATABASE VERIFICATION")

        report["loaded_rows"]["mysql"] = (
            get_mysql_database_counts()
        )

        report["loaded_rows"]["sqlite"] = (
            get_database_counts()
        )

        logger.info(
            "MYSQL DATABASE COUNTS: %s",
            report["loaded_rows"]["mysql"]
        )

        logger.info(
            "SQLITE DATABASE COUNTS: %s",
            report["loaded_rows"]["sqlite"]
        )


        # ------------------------------------------
        # PIPELINE SUCCESS
        # ------------------------------------------

        report["status"] = "SUCCESS"

        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")


    except Exception as error:

        report["status"] = "FAILED"

        report["error"] = str(error)

        logger.exception("ETL PIPELINE FAILED")


    finally:

        end_time = datetime.now(timezone.utc)

        duration = time.perf_counter() - start_clock

        report["end_time"] = end_time.isoformat()

        report["duration_seconds"] = round(duration, 3)
        # ------------------------------------------
        # SAVE MYSQL AUDIT HISTORY
        # ------------------------------------------

        if audit_started:

            try:

                complete_pipeline_audit(
                    run_id=run_id,
                    started_at=audit_started_at,
                    completed_at=datetime.now(),
                    duration_seconds=round(duration, 3),
                    status=report["status"],
                    source_data=source_data,
                    valid_data=valid_data,
                    basic_rejections=basic_rejections,
                    referential_rejections=referential_rejections,
                    transformed_data=transformed_data,
                    failure_reason=report["error"]
                )

                logger.info("MYSQL AUDIT HISTORY SAVED")

            except Exception as audit_error:

                report["status"] = "FAILED"
                report["error"] = (
                    f"Audit tracking failed: {audit_error}"
                )

                logger.exception("MYSQL AUDIT TRACKING FAILED")

        try:

            save_report(report)

            logger.info("Report saved: %s", REPORT_FILE)

        except Exception:

            logger.exception("FAILED TO SAVE PIPELINE REPORT")

        logger.info("Run status: %s", report["status"])

        logger.info(
            "Duration: %s seconds",
            report["duration_seconds"]
        )

        logger.info("=" * 60)

    return report


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    result = run_pipeline()

    print("\nFINAL PIPELINE SUMMARY")

    print("Run ID:", result["run_id"])

    print("Status:", result["status"])

    print("Duration:", result["duration_seconds"], "seconds")

    print("\nSource Records:")
    print(result["source_rows"])

    print("\nValid Records:")
    print(result["valid_rows"])

    print("\nRejected Records:")
    print(result["rejected_rows"])

    print("\nTransformed Records:")
    print(result["transformed_rows"])

    print("\nMYSQL WAREHOUSE RECORDS:")
    print(result["loaded_rows"]["mysql"])

    print("\nSQLITE BACKUP RECORDS:")
    print(result["loaded_rows"]["sqlite"])

    print("\nError:")
    print(result["error"])

    if result["status"] != "SUCCESS":
        sys.exit(1)
