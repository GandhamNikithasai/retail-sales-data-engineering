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
## Run and Verify the ETL Pipeline Using Docker

After cloning the repository and configuring your `.env` file, make sure Docker Desktop is running.

### 1. Check Docker containers

Run the following command to verify that MySQL and the dashboard containers are running:

```powershell
docker compose ps
```

Expected services:
- `retail_mysql` – MySQL database (healthy)
- `retail_dashboard` – Streamlit dashboard (running)

### 2. Execute the ETL pipeline

Run the ETL pipeline inside the Docker dashboard container:

```powershell
docker compose exec dashboard python -m src.pipeline
```

The pipeline performs the following operations:

1. Extracts data from source CSV files.
2. Validates incoming records.
3. Performs referential integrity checks.
4. Transforms the validated data.
5. Loads data into the MySQL data warehouse.
6. Loads data into the SQLite backup warehouse.
7. Generates pipeline audit information and a run summary.

### 3. Verify the MySQL database

To view the database tables, run:

```powershell
docker compose exec mysql mysql -u retail_app -p yottaflex_retail_dw -e "SHOW TABLES;"
```

To check the number of loaded sales records:

```powershell
docker compose exec mysql mysql -u retail_app -p yottaflex_retail_dw -e "SELECT COUNT(*) AS total_sales FROM fact_sales;"
```

Enter the MySQL application password when prompted.

### 4. Access the Streamlit Dashboard

Open the following URL in your browser:

```text
http://localhost:8503
```

The Retail Sales Analytics Dashboard provides access to sales analytics and warehouse information.

### 5. Run automated tests

Execute the test suite inside Docker:

```powershell
docker compose exec dashboard python -m pytest -v
```

### 6. Stop Docker containers

When finished, run:

```powershell
docker compose down
```

**Note:** The Docker Compose configuration uses a persistent MySQL volume. Stopping the containers does not delete the stored MySQL data. Donot use docker compose down -v unless you intentionally want to remove that volume.
## Run and Verify the ETL Pipeline Using Docker

### Prerequisites

Before running the project, make sure you have installed:

- Docker Desktop
- Git
- A GitHub account

Make sure Docker Desktop is running before executing the commands.

### 1. Clone the GitHub Repository

Open PowerShell and run:

```powershell
git clone https://github.com/GandhamNikithasai/retail-sales-data-engineering.git
cd retail-sales-data-engineering
```

### 2. Configure Environment Variables

Create a `.env` file in the project root directory.

If the repository includes a `.env.example` file, copy it:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure your own MySQL database credentials. Never upload your actual `.env` file or passwords to GitHub.

### 3. Start the Docker Containers

Build and start the MySQL database and Streamlit dashboard:

```powershell
docker compose up -d --build
```

### 4. Check Docker Container Status

Run:

```powershell
docker compose ps
```

Expected services:

- `retail_mysql` – MySQL database (healthy)
- `retail_dashboard` – Streamlit dashboard (running)

### 5. Execute the ETL Pipeline

Run the ETL pipeline inside the Docker dashboard container:

```powershell
docker compose exec dashboard python -m src.pipeline
```

The pipeline performs the following operations:

1. Extracts data from source CSV files.
2. Validates incoming records.
3. Performs referential integrity checks.
4. Transforms validated data.
5. Loads data into the MySQL data warehouse.
6. Loads data into the SQLite warehouse.
7. Generates pipeline audit information and a run summary.

### 6. Verify the MySQL Database

View the database tables:

```powershell
docker compose exec mysql mysql -u retail_app -p yottaflex_retail_dw -e "SHOW TABLES;"
```

Check the number of loaded sales records:

```powershell
docker compose exec mysql mysql -u retail_app -p yottaflex_retail_dw -e "SELECT COUNT(*) AS total_sales FROM fact_sales;"
```

Enter the MySQL application password when prompted.

### 7. Access the Streamlit Dashboard

Open this URL in your browser:

```text
http://localhost:8503
```

### 8. Run Automated Tests

Execute the test suite inside Docker:

```powershell
docker compose exec dashboard python -m pytest -v
```

### 9. Stop Docker Containers

When finished, run:

```powershell
docker compose down
```

**Note:** Docker Compose uses a persistent MySQL volume. Stopping the containers does not delete stored MySQL data. Do not use `docker compose down -v` unless you intentionally want to delete the database volume.



# 🚀 How to Run the Project (Reviewer Guide)

Follow the steps below to download, set up, and run the **Retail Sales Data Engineering Project** on a Windows laptop.

## 1. Download the Project

1. Open the GitHub repository:
   https://github.com/GandhamNikithasai/retail-sales-data-engineering
2. Click the green **Code** button.
3. Select **Download ZIP**.
4. Extract the downloaded ZIP file.
5. Open the extracted `retail-sales-data-engineering-main` folder.

## 2. Open the Project in VS Code

1. Open Visual Studio Code.
2. Click **File → Open Folder**.
3. Select the extracted project folder.
4. Click **Select Folder**.
5. Open the terminal using **Terminal → New Terminal**.
6. Make sure the terminal is using PowerShell and is located in the project root directory.

## 3. Check Python Installation

Python is required to execute this project.

Open PowerShell and execute:

```powershell
python --version
```

If Python is not installed, download and install it:

https://www.python.org/downloads/

During installation, select **Add Python to PATH**.

Restart VS Code after installation.

## 4. Create a Virtual Environment

Execute the following commands in PowerShell:

```powershell
python -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1
```

## 5. Install Project Dependencies

Upgrade pip and install the required Python packages:

```powershell
python -m pip install --upgrade pip

pip install -r requirements.txt
```

This installs the libraries required by the project, including Pandas, Streamlit, Plotly, Pytest, and MySQL Connector.

## 6. Run the Streamlit Dashboard

To launch the Retail Sales Analytics Dashboard, execute:

```powershell
python -m streamlit run dashboard.py --server.port 8503
```

Wait until Streamlit starts successfully.

Open your browser and visit:

**http://localhost:8503**

The Retail Sales Analytics Dashboard will be displayed.

## 7. Run the ETL Pipeline (Optional)

To execute the complete ETL pipeline, a running MySQL Server and a configured database are required.

Set the MySQL connection details in PowerShell:

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_DATABASE = "yottaflex_retail_dw"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "YOUR_MYSQL_PASSWORD"
```

Execute the ETL pipeline:

```powershell
python -m src.pipeline
```

The pipeline performs data ingestion, validation, transformation, and database loading.

**Note:** Replace `YOUR_MYSQL_PASSWORD` with the password configured for your local MySQL Server.

## 8. Run Automated Tests

To execute the project tests:

```powershell
python -m pytest -v
```

## 9. View Generated Reports

The project generates reports and execution information in the reports directory.

To view the pipeline execution summary:

```powershell
Get-Content .\reports\run_summary.json
```

To open the SQL analytics file:

```powershell
code .\reports\analytics.sql
```

## 10. Stop the Dashboard

To stop the running Streamlit application, return to PowerShell and press:

```text
Ctrl + C
```

---

## Software Requirements

| Software | Purpose |
|---|---|
| Windows 10/11 | Operating System |
| Python 3.12 | Python Runtime |
| Visual Studio Code | Code Editor |
| PowerShell | Command Execution |
| MySQL Server | Data Warehouse |
| Streamlit | Interactive Dashboard |

**Important Notes:**
- Docker is not required for this manual setup.
- Git is not required because the project can be downloaded as a ZIP file.
- Python dependencies must be installed before running the application.
- The dashboard requires the SQLite database and its expected data tables to be available.
- The complete ETL pipeline requires a running and properly configured MySQL Server.

**GitHub Repository:**  
https://github.com/GandhamNikithasai/retail-sales-data-engineering