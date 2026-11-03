
CREATE DATABASE IF NOT EXISTS yottaflex_retail_dw;
USE yottaflex_retail_dw;

-- 1. Customer dimension
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key BIGINT NOT NULL PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    customer_id VARCHAR(100) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    city VARCHAR(150),
    region VARCHAR(150),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE KEY uq_customer_source_id (source_system, customer_id)
) ENGINE=InnoDB;

-- 2. Product dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_key BIGINT NOT NULL PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(150),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE KEY uq_product_source_id (source_system, product_id)
) ENGINE=InnoDB;

-- 3. Date dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT NOT NULL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_number INT NOT NULL,
    month_number INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter_number INT NOT NULL,
    year_number INT NOT NULL,
    weekday_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
) ENGINE=InnoDB;

-- 4. Sales fact table
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGINT NOT NULL PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    order_item_id VARCHAR(100) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,
    date_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    gross_sales DECIMAL(14,2) NOT NULL,
    discount_amount DECIMAL(14,2) NOT NULL,
    net_sales DECIMAL(14,2) NOT NULL,
    order_status VARCHAR(30) NOT NULL,

    UNIQUE KEY uq_sales_source_item (source_system, order_item_id),
    INDEX idx_sales_customer (customer_key),
    INDEX idx_sales_product (product_key),
    INDEX idx_sales_date (date_key),
    INDEX idx_sales_order (order_id),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
) ENGINE=InnoDB;

-- 5. Pipeline audit table
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR(36) NOT NULL PRIMARY KEY,
    source_file VARCHAR(255) NOT NULL,
    started_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    duration_seconds DECIMAL(12,3) DEFAULT 0,
    status VARCHAR(30) NOT NULL,
    input_records BIGINT DEFAULT 0,
    valid_records BIGINT DEFAULT 0,
    duplicate_records BIGINT DEFAULT 0,
    rejected_records BIGINT DEFAULT 0,
    loaded_records BIGINT DEFAULT 0,
    failure_reason TEXT NULL
) ENGINE=InnoDB;

-- 6. Ingestion history table
CREATE TABLE IF NOT EXISTS ingestion_history (
    ingestion_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    file_checksum CHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    ingestion_started_at DATETIME NOT NULL,
    ingestion_completed_at DATETIME NOT NULL,
    input_records BIGINT DEFAULT 0,
    valid_records BIGINT DEFAULT 0,
    rejected_records BIGINT DEFAULT 0,
    status VARCHAR(30) NOT NULL,
    error_message TEXT NULL,

    INDEX idx_ingestion_run (run_id),

    CONSTRAINT fk_ingestion_run
        FOREIGN KEY (run_id)
        REFERENCES pipeline_runs(run_id)
) ENGINE=InnoDB;

-- 7. Rejected records table
CREATE TABLE IF NOT EXISTS rejected_records (
    rejection_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    source_record_id VARCHAR(100) NULL,
    original_record LONGTEXT NOT NULL,
    rejection_reason TEXT NOT NULL,

    INDEX idx_rejected_run (run_id),

    CONSTRAINT fk_rejected_run
        FOREIGN KEY (run_id)
        REFERENCES pipeline_runs(run_id)
) ENGINE=InnoDB;
