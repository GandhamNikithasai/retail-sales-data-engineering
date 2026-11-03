
-- 1. Total Sales Revenue
SELECT
    ROUND(SUM(net_amount), 2) AS total_revenue
FROM fact_sales;


-- 2. Monthly Revenue
SELECT
    d.year,
    d.month,
    ROUND(SUM(f.net_amount), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;


-- 3. Region-wise Revenue
SELECT
    c.region,
    ROUND(SUM(f.net_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY c.region
ORDER BY total_revenue DESC;


-- 4. Top 5 Products by Revenue
SELECT
    p.product_name,
    p.category,
    SUM(f.quantity) AS total_quantity_sold,
    ROUND(SUM(f.net_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;


-- 5. Average Order Value (AOV)
SELECT
    ROUND(
        SUM(net_amount) / COUNT(DISTINCT order_id),
        2
    ) AS average_order_value
FROM fact_sales;


-- 6. Total Completed Orders
SELECT
    COUNT(DISTINCT order_id) AS completed_orders
FROM fact_sales;
