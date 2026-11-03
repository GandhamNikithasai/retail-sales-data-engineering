# Retail Sales Data Engineering Project

## 1. Project Overview

This project implements a retail sales data engineering pipeline. It ingests retail CSV files, validates and transforms the data, loads analytical warehouse tables, records execution information, and provides a Streamlit dashboard for sales analysis.

The project uses Python, Pandas, MySQL, SQLite, SQL, and Streamlit.

## 2. Main Features

- CSV ingestion for customers, products, orders, and order items.
- Data validation and rejection handling.
- Referential integrity checks.
- Dimensional data transformation.
- MySQL data warehouse loading.
- SQLite warehouse storage.
- Pipeline audit and execution summaries.
- Sales analytics using SQL.
- Interactive Streamlit dashboard.
- Configurable synthetic data generation.
- Performance testing with a 100,000-order dataset.
- Automated testing using pytest.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | ETL implementation |
| Pandas | Data processing |
| MySQL | Analytical warehouse |
| SQLite | Local warehouse |
| SQL | Analytics and data verification |
| Streamlit | Dashboard |
| Pytest | Automated testing |

## 4. Project Structure

```text
retail_sales_data_engineering/
|
|-- dashboard.py
|-- requirements.txt
|-- README.md
|
|-- docs/
|   |-- DATA_DICTIONARY.md
|   |-- ARCHITECTURE.md
|
|-- src/
|   |-- audit.py
|   |-- data_entry.py
|   |-- generate_data.py
|   |-- ingestion.py
|   |-- loading.py
|   |-- mysql_connection.py
|   |-- mysql_loading.py
|   |-- performance_test.py
|   |-- pipeline.py
|   |-- referential_validation.py
|   |-- run_analytics.py
|   |-- transformation.py
|   |-- validation.py
|
|-- tests/
|   |-- test_warehouse.py
|
|-- data/
|   |-- raw/
|   |-- performance_test/
|   |-- warehouse.db
|
|-- database/
|-- logs/
|-- reports/
    |-- analytics.sql
    |-- run_summary.json
```

## 5. Input Data

The pipeline uses four CSV files:

- `customers.csv`
- `products.csv`
- `orders.csv`
- `order_items.csv`

The files are stored in `data/raw/`.

## 6. Setup

Open PowerShell in the project root.

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure the MySQL connection using environment variables. Replace the password placeholder locally with your own MySQL password. Do not commit credentials to Git.

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_DATABASE = "yottaflex_retail_dw"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "YOUR_MYSQL_PASSWORD"
```

## 7. Run the ETL Pipeline

From the project root:

```powershell
python -m src.pipeline
```

The pipeline performs ingestion, validation, referential checks, transformation, database loading, and audit reporting.

## 8. Run the Dashboard

```powershell
streamlit run dashboard.py --server.port 8503
```

Open the dashboard in a browser:

http://localhost:8503

The dashboard provides sales KPIs, date filtering, revenue analysis, regional analysis, product analysis, tabular details, and data export features.

## 9. Generate Synthetic Data

Example command to generate a larger performance dataset:

```powershell
python .\src\generate_data.py --orders 100000 --start-date 2025-02-01 --end-date 2026-10-31 --seed 42 --output-dir .\data\performance_test\raw
```

This writes the performance dataset separately from the regular input data.

## 10. Run the Performance Test

```powershell
python -m src.performance_test
```

The performance test measures ingestion and transformation time, memory usage, throughput, missing key mappings, invalid sales records, and duplicate fact records. It does not load the performance dataset into the databases.

## 11. Run Automated Tests

```powershell
python -m pytest -v
```

## 12. SQL Analytics

SQL analytics queries are maintained in:

`reports/analytics.sql`

The queries use warehouse fact and dimension tables for sales analysis.

## 13. Audit and Reports

Pipeline execution information is maintained through the audit module and report outputs, including:

`reports/run_summary.json`

Log files are stored in the `logs/` directory.

## 14. Data Safety

- Keep database credentials outside source code.
- Do not delete existing warehouse records as part of routine verification.
- Keep performance test data separate from regular raw input data.
- Review validation and audit results after pipeline execution.
- Back up database files before making schema or data changes.

## 15. Project Status

The ETL pipeline, dashboard, historical date reconciliation, idempotency checks, data-quality checks, and 100,000-order transformation performance test have been exercised during development.

The latest recorded performance test processed 299,852 source rows and produced 149,963 fact rows. It reported zero missing foreign-key mappings, zero invalid sales records, and zero duplicate fact records.

Automated tests previously reported 8 passed. Re-run the tests in the current environment before publishing the final project.

## 16. Future Enhancements

- Cloud deployment.
- Automated scheduled pipeline execution.
- CI/CD integration.
- Additional monitoring and alerting.
- Incremental loading improvements.
