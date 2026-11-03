
import subprocess
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.mysql_connection import create_mysql_connection

from src.data_entry import (
    add_customer,
    add_product,
    add_order,
    add_order_item,
    read_csv
)


# =========================================================
# 1. PROJECT CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Retail Sales Analytics Dashboard")

st.caption(
    "Retail Sales Data Warehouse and Analytics Pipeline"
)


# =========================================================
# 2. MYSQL QUERY FUNCTION
# =========================================================

def read_mysql_query(query, params=None):

    """Execute a MySQL query and return a DataFrame."""

    connection = create_mysql_connection()
    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())

        rows = cursor.fetchall()

        return pd.DataFrame(rows)

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()


# =========================================================
# 3. RUN ETL PIPELINE AFTER FORM SUBMISSION
# =========================================================

def save_and_publish(save_function, *args):

    try:

        message = save_function(*args)

        st.success(message)

        with st.spinner(
            "Running ETL pipeline and updating warehouses..."
        ):

            result = subprocess.run(
                [sys.executable, "-m", "src.pipeline"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=600
            )

        if result.returncode == 0:

            st.success(
                "ETL completed successfully. Warehouses updated!"
            )

            st.cache_data.clear()

            st.rerun()

        else:

            st.error(
                "The record was saved in the source CSV, "
                "but the ETL pipeline failed."
            )

            st.warning(
                "Do not submit the same record again. "
                "Check the pipeline output before retrying."
            )

            with st.expander("View ETL Pipeline Output"):

                st.code(
                    (result.stdout or "")
                    + "\n"
                    + (result.stderr or "")
                )

    except subprocess.TimeoutExpired:

        st.error(
            "ETL exceeded the 10-minute timeout. "
            "Check the pipeline logs."
        )

    except Exception as error:

        st.error(f"Unable to save the record: {error}")


# =========================================================
# 4. LOAD SOURCE CSV DATA
# =========================================================

try:

    customers_source = read_csv("customers")
    products_source = read_csv("products")
    orders_source = read_csv("orders")
    order_items_source = read_csv("order_items")

    customer_ids = sorted(
        customers_source["customer_id"].astype(str).tolist()
    )

    product_ids = sorted(
        products_source["product_id"].astype(str).tolist()
    )

    order_ids = sorted(
        orders_source["order_id"].astype(str).tolist()
    )

except Exception as error:

    st.error(f"Unable to load source data: {error}")

    st.stop()


# =========================================================
# 5. DATA ENTRY FORMS
# =========================================================

st.divider()

st.header("➕ Enter New Retail Data")

st.caption(
    "Add records to your source CSV files and publish them "
    "through the ETL pipeline."
)


# ---------------------------------------------------------
# CUSTOMER FORM
# ---------------------------------------------------------

with st.expander("Add New Customer"):

    with st.form("customer_form"):

        customer_id = st.text_input(
            "Customer ID",
            placeholder="Example: C0102"
        )

        customer_name = st.text_input("Customer Name")

        city = st.text_input("City")

        region = st.text_input("Region")

        submit_customer = st.form_submit_button(
            "Save Customer",
            use_container_width=True
        )

        if submit_customer:

            save_and_publish(
                add_customer,
                customer_id,
                customer_name,
                city,
                region
            )


# ---------------------------------------------------------
# PRODUCT FORM
# ---------------------------------------------------------

with st.expander("Add New Product"):

    with st.form("product_form"):

        product_id = st.text_input(
            "Product ID",
            placeholder="Example: P0031"
        )

        product_name = st.text_input("Product Name")

        category = st.text_input(
            "Category",
            placeholder="Example: Clothing"
        )

        unit_price = st.number_input(
            "Unit Price",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

        submit_product = st.form_submit_button(
            "Save Product",
            use_container_width=True
        )

        if submit_product:

            save_and_publish(
                add_product,
                product_id,
                product_name,
                category,
                unit_price
            )


# ---------------------------------------------------------
# ORDER FORM
# ---------------------------------------------------------

with st.expander("Add New Order"):

    if not customer_ids:

        st.warning("Add a customer before creating an order.")

    else:

        with st.form("order_form"):

            order_id = st.text_input(
                "Order ID",
                placeholder="Example: O002001"
            )

            selected_customer = st.selectbox(
                "Select Customer",
                customer_ids
            )

            order_date = st.date_input(
                "Order Date",
                value=date.today()
            )

            order_status = st.selectbox(
                "Order Status",
                ["Completed", "Pending", "Cancelled"]
            )

            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Card", "UPI", "Net Banking"]
            )

            submit_order = st.form_submit_button(
                "Save Order",
                use_container_width=True
            )

            if submit_order:

                save_and_publish(
                    add_order,
                    order_id,
                    selected_customer,
                    order_date,
                    order_status,
                    payment_method
                )


# ---------------------------------------------------------
# ORDER ITEM FORM
# ---------------------------------------------------------

with st.expander("Add New Order Item"):

    if not order_ids or not product_ids:

        st.warning(
            "Add at least one order and one product first."
        )

    else:

        with st.form("order_item_form"):

            order_item_id = st.text_input(
                "Order Item ID",
                placeholder="Example: OI00003989"
            )

            selected_order = st.selectbox(
                "Select Order",
                order_ids
            )

            selected_product = st.selectbox(
                "Select Product",
                product_ids
            )

            selected_product_row = products_source[
                products_source["product_id"].astype(str)
                == selected_product
            ]

            default_price = float(
                selected_product_row.iloc[0]["unit_price"]
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=1,
                step=1
            )

            item_unit_price = st.number_input(
                "Unit Price",
                min_value=0.0,
                value=default_price,
                step=10.0
            )

            discount_amount = st.number_input(
                "Discount Amount",
                min_value=0.0,
                value=0.0,
                step=10.0
            )

            submit_item = st.form_submit_button(
                "Save Order Item",
                use_container_width=True
            )

            if submit_item:

                save_and_publish(
                    add_order_item,
                    order_item_id,
                    selected_order,
                    selected_product,
                    quantity,
                    item_unit_price,
                    discount_amount
                )


# =========================================================
# 6. SOURCE DATA COUNTS
# =========================================================

st.divider()

st.subheader("Source Data Record Counts")

count1, count2, count3, count4 = st.columns(4)

count1.metric("Customers", len(customers_source))
count2.metric("Products", len(products_source))
count3.metric("Orders", len(orders_source))
count4.metric("Order Items", len(order_items_source))


# =========================================================
# 7. MYSQL DATA RANGE
# =========================================================

@st.cache_data(ttl=60)
def get_available_dates():

    result = read_mysql_query("""
        SELECT
            MIN(d.full_date) AS min_date,
            MAX(d.full_date) AS max_date
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
    """)

    if result.empty or pd.isna(result.loc[0, "min_date"]):

        return None, None

    return (
        pd.to_datetime(result.loc[0, "min_date"]).date(),
        pd.to_datetime(result.loc[0, "max_date"]).date()
    )


# =========================================================
# 8. DATE FILTER SECTION
# =========================================================

st.divider()

st.header("📅 Analytics Date Filters")

try:

    minimum_date, maximum_date = get_available_dates()

except Exception as error:

    st.error(f"Unable to retrieve available dates: {error}")

    st.stop()


if minimum_date is None:

    st.warning("No sales records are available in the warehouse.")

    st.stop()


with st.form("date_filter_form"):

    date_col1, date_col2 = st.columns(2)

    with date_col1:

        start_date = st.date_input(
            "Start Date",
            value=minimum_date,
            min_value=minimum_date,
            max_value=maximum_date
        )

    with date_col2:

        end_date = st.date_input(
            "End Date",
            value=maximum_date,
            min_value=minimum_date,
            max_value=maximum_date
        )

    apply_filter = st.form_submit_button(
        "Apply Date Filter",
        use_container_width=True
    )


if start_date > end_date:

    st.error("Start date cannot be later than end date.")

    st.stop()


st.caption(
    f"Showing sales from {start_date} to {end_date}"
)


# =========================================================
# 9. LOAD FILTERED ANALYTICS FROM MYSQL
# =========================================================

@st.cache_data(ttl=60)
def load_data(start_date, end_date):

    date_params = (start_date, end_date)

    # -----------------------------------------------------
    # KPI QUERY
    # -----------------------------------------------------

    kpis = read_mysql_query("""

        SELECT

            ROUND(
                COALESCE(SUM(f.net_sales), 0),
                2
            ) AS revenue,

            COUNT(
                DISTINCT f.order_id
            ) AS total_orders,

            ROUND(
                COALESCE(SUM(f.net_sales), 0) /
                NULLIF(COUNT(DISTINCT f.order_id), 0),
                2
            ) AS average_order_value,

            COALESCE(
                SUM(f.quantity),
                0
            ) AS units_sold

        FROM fact_sales f

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE d.full_date BETWEEN %s AND %s

    """, date_params)


    # -----------------------------------------------------
    # MONTHLY REVENUE QUERY
    # -----------------------------------------------------

    monthly = read_mysql_query("""

        SELECT

            d.year_number AS year,

            d.month_number AS month,

            ROUND(
                SUM(f.net_sales),
                2
            ) AS revenue

        FROM fact_sales f

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE d.full_date BETWEEN %s AND %s

        GROUP BY
            d.year_number,
            d.month_number

        ORDER BY
            d.year_number,
            d.month_number

    """, date_params)


    # -----------------------------------------------------
    # REGION-WISE REVENUE QUERY
    # -----------------------------------------------------

    regional = read_mysql_query("""

        SELECT

            c.region,

            ROUND(
                SUM(f.net_sales),
                2
            ) AS revenue

        FROM fact_sales f

        JOIN dim_customer c
            ON f.customer_key = c.customer_key

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE d.full_date BETWEEN %s AND %s

        GROUP BY c.region

        ORDER BY revenue DESC

    """, date_params)


    # -----------------------------------------------------
    # TOP 5 PRODUCTS QUERY
    # -----------------------------------------------------

    products = read_mysql_query("""

        SELECT

            p.product_name,

            SUM(f.quantity) AS quantity_sold,

            ROUND(
                SUM(f.net_sales),
                2
            ) AS revenue

        FROM fact_sales f

        JOIN dim_product p
            ON f.product_key = p.product_key

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE d.full_date BETWEEN %s AND %s

        GROUP BY
            p.product_key,
            p.product_name

        ORDER BY revenue DESC

        LIMIT 5

    """, date_params)


    # -----------------------------------------------------
    # DETAILED SALES TRANSACTIONS
    # -----------------------------------------------------

    sales_details = read_mysql_query("""

        SELECT

            f.order_id,

            f.order_item_id,

            d.full_date AS order_date,

            c.customer_id,

            c.customer_name,

            c.region,

            p.product_id,

            p.product_name,

            p.category,

            f.quantity,

            f.unit_price,

            f.gross_sales,

            f.discount_amount,

            f.net_sales,

            f.order_status

        FROM fact_sales f

        JOIN dim_date d
            ON f.date_key = d.date_key

        JOIN dim_customer c
            ON f.customer_key = c.customer_key

        JOIN dim_product p
            ON f.product_key = p.product_key

        WHERE d.full_date BETWEEN %s AND %s

        ORDER BY
            d.full_date DESC,
            f.order_id

        LIMIT 10000

    """, date_params)


    return (
        kpis,
        monthly,
        regional,
        products,
        sales_details
    )


# =========================================================
# 10. EXECUTE MYSQL ANALYTICS
# =========================================================

try:

    (
        kpis,
        monthly,
        regional,
        products,
        sales_details

    ) = load_data(start_date, end_date)

except Exception as error:

    st.error(
        f"Unable to load analytics from MySQL: {error}"
    )

    st.stop()


# =========================================================
# 11. KPI CARDS
# =========================================================

st.divider()

st.header("Business Performance")

col1, col2, col3, col4 = st.columns(4)

revenue = kpis.loc[0, "revenue"]

total_orders = kpis.loc[0, "total_orders"]

average_order_value = kpis.loc[
    0,
    "average_order_value"
]

units_sold = kpis.loc[0, "units_sold"]


col1.metric(
    "Total Revenue",
    f"₹{float(revenue):,.2f}"
)

col2.metric(
    "Completed Orders",
    f"{int(total_orders):,}"
)

col3.metric(
    "Average Order Value",
    (
        f"₹{float(average_order_value):,.2f}"
        if pd.notna(average_order_value)
        else "₹0.00"
    )
)

col4.metric(
    "Units Sold",
    f"{int(units_sold):,}"
)


# =========================================================
# 12. MONTHLY REVENUE CHART
# =========================================================

st.divider()

st.subheader("Monthly Revenue Trend")

if not monthly.empty:

    monthly["month_label"] = (
        monthly["year"].astype(str)
        + "-"
        + monthly["month"].astype(str).str.zfill(2)
    )

    monthly_chart = px.line(
        monthly,
        x="month_label",
        y="revenue",
        markers=True,
        title="Revenue by Month"
    )

    monthly_chart.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (₹)"
    )

    st.plotly_chart(
        monthly_chart,
        use_container_width=True
    )

else:

    st.info("No monthly revenue data available.")


# =========================================================
# 13. REGION AND PRODUCT CHARTS
# =========================================================

left, right = st.columns(2)


with left:

    st.subheader("Region-wise Revenue")

    if not regional.empty:

        region_chart = px.bar(
            regional,
            x="region",
            y="revenue",
            title="Revenue by Region"
        )

        region_chart.update_layout(
            xaxis_title="Region",
            yaxis_title="Revenue (₹)"
        )

        st.plotly_chart(
            region_chart,
            use_container_width=True
        )

    else:

        st.info("No regional data available.")


with right:

    st.subheader("Top 5 Products")

    if not products.empty:

        product_chart = px.bar(
            products,
            x="revenue",
            y="product_name",
            orientation="h",
            title="Top Products by Revenue"
        )

        product_chart.update_layout(
            xaxis_title="Revenue (₹)",
            yaxis_title="Product"
        )

        st.plotly_chart(
            product_chart,
            use_container_width=True
        )

    else:

        st.info("No product data available.")


# =========================================================
# 14. PRODUCT AND REGIONAL SUMMARY TABLES
# =========================================================

st.divider()

st.header("📋 Summary Tables")

st.subheader("Top Product Details")

st.dataframe(
    products,
    use_container_width=True,
    hide_index=True
)


st.subheader("Regional Revenue Details")

st.dataframe(
    regional,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 15. DETAILED SALES TRANSACTION TABLE
# =========================================================

st.divider()

st.header("🧾 Detailed Sales Transactions")

st.caption(
    "Sales records for the selected date range. "
    "The table displays up to 10,000 records."
)

if not sales_details.empty:

    st.metric(
        "Displayed Sales Records",
        f"{len(sales_details):,}"
    )

    st.dataframe(
        sales_details,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # CSV EXPORT
    # -----------------------------------------------------

    csv_data = sales_details.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Sales Data as CSV",
        data=csv_data,
        file_name="retail_sales_report.csv",
        mime="text/csv",
        use_container_width=True
    )

else:

    st.info(
        "No sales transactions found for the selected date range."
    )


# =========================================================
# 16. FOOTER
# =========================================================

st.divider()

st.caption(
    "Analytics source: MySQL Retail Data Warehouse | "
    "Data entry: Raw CSV files | "
    "Backup warehouse: SQLite"
)
