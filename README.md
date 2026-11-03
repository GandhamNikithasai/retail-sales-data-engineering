# 🛒 Retail Sales Data Engineering Project

**An End-to-End Retail Sales ETL Pipeline with Data Validation, Data Warehousing, SQL Analytics, and Interactive Dashboard**

---

## 1. Project Overview

The **Retail Sales Data Engineering Project** is an end-to-end data engineering solution designed to process retail sales data and convert raw data into meaningful business insights.

The project implements an ETL (Extract, Transform, Load) pipeline using Python and Pandas. It extracts retail data from CSV files, performs data cleaning, validation, transformation, and loads the processed data into MySQL and SQLite databases.

It also generates SQL analytics, maintains pipeline execution logs and audit reports, and provides an interactive Streamlit dashboard to visualize retail sales performance.

The main objective of this project is to demonstrate how raw retail data can be transformed into structured, reliable, and analytics-ready data.

## 2. Project Objectives

- Develop an end-to-end ETL pipeline.
- Extract retail data from multiple CSV files.
- Perform data cleaning and validation.
- Identify missing, invalid, and duplicate records.
- Implement referential integrity checks.
- Transform raw data into dimensional warehouse tables.
- Load processed data into MySQL and SQLite.
- Maintain pipeline execution logs and audit reports.
- Perform SQL-based business analytics.
- Develop an interactive sales dashboard.
- Perform automated testing and performance testing.

## 3. Technologies Used

| Technology | Purpose |
| ---------- | ------- |
| Python | ETL pipeline development |
| Pandas | Data cleaning and transformation |
| MySQL | Analytical data warehouse |
| SQLite | Local warehouse storage |
| SQL | Data analysis and validation |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| Pytest | Automated testing |
| PowerShell | Project execution on Windows |
| VS Code | Development environment |
| GitHub | Project hosting and version control |

## 4. Project Architecture

The project follows an ETL architecture.

```text
                RETAIL SALES CSV FILES
                         |
                         v
                  DATA INGESTION
                         |
                         v
                 DATA VALIDATION
                         |
                         v
              REFERENTIAL VALIDATION
                         |
                         v
                DATA TRANSFORMATION
                         |
                         v
                 DATA WAREHOUSING
                    /         \
                   v           v
                MySQL        SQLite
                   \           /
                    \         /
                     v       v
                   SQL ANALYTICS
                         |
                         v
                  AUDIT & REPORTS
                         |
                         v
                STREAMLIT DASHBOARD
                         |
                         v
                  BUSINESS INSIGHTS
```

## 5. Main Features

### 5.1 Data Ingestion

- Reads multiple retail CSV files.
- Loads customer, product, order, and order-item information.
- Organizes the raw input data for processing.

### 5.2 Data Validation

- Checks missing values.
- Identifies invalid records.
- Detects duplicate records.
- Validates required fields.
- Checks data consistency.

### 5.3 Referential Integrity Validation

- Validates customer references.
- Validates product references.
- Checks relationships between orders and order items.
- Identifies records with invalid references.

### 5.4 Data Transformation

- Cleans raw retail data.
- Standardizes data formats.
- Applies business rules.
- Creates structured analytical datasets.
- Prepares fact and dimension tables.

### 5.5 Data Warehousing

- Loads processed data into MySQL.
- Maintains a local SQLite warehouse.
- Organizes data into analytical tables.
- Supports SQL-based reporting and analysis.

### 5.6 Audit and Logging

- Records pipeline execution details.
- Maintains execution summaries.
- Tracks processing information.
- Stores logs and reports.

### 5.7 Interactive Dashboard

- Displays sales KPIs.
- Provides date-based filtering.
- Visualizes revenue trends.
- Displays regional sales analysis.
- Provides product-level analysis.
- Supports tabular data exploration and export.

### 5.8 Testing and Performance

- Automated testing using Pytest.
- Data quality verification.
- Duplicate and invalid-record checks.
- Performance testing using a larger synthetic dataset.

## 6. Project Folder Structure

```text
retail-sales-data-engineering/
│
├── data/
│   ├── raw/
│   ├── performance_test/
│   └── warehouse.db
│
├── database/
│   ├── mysql/
│   │   └── init.sql
│   └── warehouse.db
│
├── reports/
│   ├── analytics.sql
│   ├── run_summary.json
│   └── reviewer_summary.json
│
├── src/
│   ├── audit.py
│   ├── data_entry.py
│   ├── generate_data.py
│   ├── ingestion.py
│   ├── loading.py
│   ├── mysql_connection.py
│   ├── mysql_loading.py
│   ├── performance_test.py
│   ├── pipeline.py
│   ├── build_reviewer_db.py
│   ├── referential_validation.py
│   ├── run_analytics.py
│   ├── transformation.py
│   └── validation.py
│
├── tests/
│   └── test_warehouse.py
│
├── AI_PROMPTS.md
├── dashboard.py
├── requirements.txt
├── dockerfile
├── compose.yaml
├── test_stage.py
└── README.md
```

## 7. Input Data

The project uses four CSV input files.

| File Name | Description |
| ---------- | ----------- |
| customers.csv | Customer information |
| products.csv | Product information |
| orders.csv | Order transaction details |
| order_items.csv | Individual products included in orders |

**Input directory:**

```text
data/raw/
```

The pipeline uses these datasets as the source for data ingestion, validation, transformation, and warehouse loading.

## 8. Installation and Execution Guide (Windows)

Follow the commands in the exact order given below.

This guide is intended for beginners and reviewers who want to download and execute the project on a Windows laptop.

### Step 1: Download the Project from GitHub

Open the project repository:

[https://github.com/GandhamNikithasai/retail-sales-data-engineering](https://github.com/GandhamNikithasai/retail-sales-data-engineering)

1. Click the green **Code** button.
2. Select **Download ZIP**.
3. Wait for the ZIP file to download.
4. Extract the downloaded ZIP file.
5. Open the extracted project folder.

### Step 2: Open the Project in VS Code

1. Open Visual Studio Code.
2. Select **File → Open Folder**.
3. Choose the extracted project folder.
4. Click **Select Folder**.
5. Open **Terminal → New Terminal**.
6. Select PowerShell.

Make sure the terminal is opened inside the project root directory.

The project root directory must contain:

```text
dashboard.py
requirements.txt
compose.yaml
src/
data/
database/
reports/
```

### Step 3: Verify and Install Python (Windows)

Python is required to execute the ETL pipeline and Streamlit dashboard.

**1. Check whether Python is installed:**

Open the VS Code PowerShell terminal and execute:

```powershell
python --version
```

Also check the Python launcher:

```powershell
py --version
```

**2. If Python is already installed:**

You should see an output similar to:

```text
Python 3.12.x
```

Continue to Step 4.

**3. If Python is not installed:**

Install Python 3.12 using Windows Package Manager:

```powershell
winget install -e --id Python.Python.3.12
```

Wait until the installation is completed.

Alternatively, download Python from the official website:

[https://www.python.org/downloads/](https://www.python.org/downloads/)

During manual installation:

- Select **Add Python to PATH**.
- Complete the installation.
- Restart VS Code.

**4. Verify Python installation again:**

Close and reopen the VS Code terminal.

Execute:

```powershell
python --version
```

```powershell
py --version
```

Expected output:

```text
Python 3.12.x
```

**5. Verify pip installation:**

```powershell
python -m pip --version
```

If Python and pip are working correctly, continue to Step 4.

### Step 4: Create a Python Virtual Environment

A virtual environment keeps the project's Python packages separate from other Python projects.

Execute:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should display:

```text
(.venv)
```

### Step 5: Upgrade pip

Execute:

```powershell
python -m pip install --upgrade pip
```

### Step 6: Install Required Dependencies

Install all the packages listed in requirements.txt:

```powershell
python -m pip install -r requirements.txt
```

The required dependencies include:

- Pandas
- Pytest
- Streamlit
- Plotly
- MySQL Connector

Wait until the installation finishes successfully.

### Step 7: Verify the Input CSV Files

Check whether the required CSV files are available:

```powershell
Get-ChildItem .\data\raw
```

The directory should contain:

```text
customers.csv
products.csv
orders.csv
order_items.csv
```

If these files are not present, generate the sample dataset using the project data-generation script.

### Step 8: Generate Synthetic Retail Sales Data (If Required)

To generate a sample dataset containing 500 orders, execute:

```powershell
python -m src.generate_data --orders 500 --start-date 2025-01-01 --end-date 2025-12-31 --seed 42 --output-dir .\data\raw
```

This generates the input CSV files in the raw data directory.

Verify the generated files:

```powershell
Get-ChildItem .\data\raw
```

**Note:** Generate the dataset only when the required input files are missing or when you want to create a fresh dataset.

### Step 9: Configure MySQL Connection

The complete ETL pipeline requires a running MySQL Server.

Create the database and configure your local MySQL connection before running the pipeline.

Set the connection details in PowerShell:

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_DATABASE = "yottaflex_retail_dw"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "YOUR_MYSQL_PASSWORD"
```

Replace `YOUR_MYSQL_PASSWORD` with your own MySQL password.

Do not upload your actual database password to GitHub.

### Step 10: Execute the Main ETL Pipeline

After completing the previous steps, execute the main pipeline:

```powershell
python -m src.pipeline
```

The pipeline performs the following operations:

1. Extracts raw retail sales data.
2. Validates the input records.
3. Performs referential integrity checks.
4. Transforms and cleans the data.
5. Loads processed data into the warehouse.
6. Updates audit and execution information.
7. Generates pipeline reports.

Wait until the pipeline execution is completed.

Review the terminal output for errors and the final execution status.

### Step 11: View the Pipeline Execution Summary

To view the execution summary:

```powershell
Get-Content .\reports\run_summary.json
```

The summary contains pipeline execution information.

### Step 12: Execute SQL Analytics

The SQL analytics queries are available in:

```text
reports/analytics.sql
```

Open the file in VS Code:

```powershell
code .\reports\analytics.sql
```

Use the queries to explore the warehouse tables and analyze retail sales information.

### Step 13: Launch the Streamlit Dashboard

After the warehouse data is available, execute:

```powershell
python -m streamlit run dashboard.py --server.port 8503
```

Wait for Streamlit to start successfully.

Open your web browser and visit:

[**http://localhost:8503**](http://localhost:8503)

The Retail Sales Analytics Dashboard will appear.

### Step 14: Explore the Dashboard

The interactive dashboard provides:

- Sales performance KPIs.
- Revenue analysis.
- Date-based filtering.
- Regional sales analysis.
- Product-level performance.
- Sales data tables.
- Data export functionality.

Explore the available filters and visualizations to understand retail business performance.

### Step 15: Run Automated Tests

To verify the project functionality, execute:

```powershell
python -m pytest -v
```

Review the test results in PowerShell.

### Step 16: Run Performance Testing (Optional)

To generate a larger performance-testing dataset:

```powershell
python .\src\generate_data.py --orders 100000 --start-date 2025-02-01 --end-date 2026-10-31 --seed 42 --output-dir .\data\performance_test\raw
```

Execute the performance test:

```powershell
python -m src.performance_test
```

This evaluates processing time, memory usage, throughput, and data-quality checks.

The performance test uses a separate dataset and does not load that dataset into the regular warehouse.

### Step 17: Stop the Dashboard

To stop the running Streamlit dashboard, return to PowerShell and press:

```text
Ctrl + C
```

## 9. Expected Project Outputs

After successful execution, the project produces the following outputs:

| Output | Description |
| ------ | ----------- |
| Processed datasets | Cleaned and transformed retail records |
| MySQL warehouse | Analytical database tables |
| SQLite database | Local warehouse storage |
| run_summary.json | Pipeline execution summary |
| analytics.sql | SQL analytics queries |
| Logs | Pipeline execution information |
| Streamlit dashboard | Interactive retail sales visualizations |
| Pytest results | Automated test results |

## 10. Database and Data Warehouse

The project uses two database systems.

**MySQL**

- Used as the analytical data warehouse.
- Stores processed retail data.
- Supports analytical queries and data verification.

**SQLite**

- Provides local database storage.
- Supports warehouse data access without requiring a separate SQLite server.

## 11. Data Quality and Validation

Data quality is an important part of the pipeline.

The project performs:

- Missing-value validation.
- Duplicate-record detection.
- Invalid-record identification.
- Referential integrity checks.
- Data consistency checks.
- Warehouse record verification.

These checks help improve the reliability and accuracy of the processed retail data.

## 12. Important Notes for Reviewers

- Docker is not required when following the manual Python setup instructions in this section.
- Git is not required because the repository can be downloaded as a ZIP file.
- Python must be installed before executing the project.
- The Python dependencies must be installed using requirements.txt.
- A running and configured MySQL Server is required for the complete ETL pipeline.
- The input CSV files must be available in `data/raw/`.
- The dashboard requires its expected warehouse data to be available.
- Keep database credentials private.
- Do not delete the existing warehouse database before reviewing the project output.

**For a fresh Windows laptop:** The manual setup requires Python, the project dependencies, and MySQL Server. VS Code and PowerShell are used to execute and inspect the project. Docker is optional for this manual workflow.

## 13. Future Enhancements

- Cloud-based deployment.
- Automated pipeline scheduling.
- Advanced data-quality monitoring.
- Additional business intelligence visualizations.
- Improved pipeline performance.
- CI/CD integration.
- Additional analytical reporting.

## 14. Developed By

**Developed by: Gandham Nikithasai**

I developed this Retail Sales Data Engineering Project to demonstrate an end-to-end data engineering workflow, starting from raw retail data ingestion to data validation, transformation, data warehousing, SQL analytics, and interactive dashboard development.

Through this project, I gained practical experience in Python programming, Pandas data processing, ETL pipeline development, MySQL, SQLite, SQL analytics, data validation, automated testing, and Streamlit dashboard development.

This project represents my practical implementation and understanding of data engineering concepts.

## 15. GitHub Repository

**Project Name:** Retail Sales Data Engineering

**Repository:**

[https://github.com/GandhamNikithasai/retail-sales-data-engineering](https://github.com/GandhamNikithasai/retail-sales-data-engineering)

Thank you for reviewing my project!
