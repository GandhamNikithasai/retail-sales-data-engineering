
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# 1. PROJECT CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "warehouse.db"

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
# 2. SQLITE CONNECTION
# =========================================================

def get_connection():

    """Connect to the prepared SQLite reviewer database."""

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Reviewer database not found: {DB_PATH}"
        )

    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def read_sqlite_query(query, params=None):

    """Execute a SQLite query and return a DataFrame."""

    connection = get_connection()

    try:
        return pd.read_sql_query(
            query,
            connection,
            params=params or ()
        )

    finally:
        connection.close()


# =========================================================
# 3. DATABASE AVAILABILITY CHECK
# =========================================================

try:

    database_check = read_sqlite_query(
        "SELECT COUNT(*) AS total FROM fact_sales"
    )

    if database_check.loc[0, "total"] == 0:
        st.error("The SQLite warehouse contains no sales records.")
        st.stop()

except Exception as error:

    st.error(f"Unable to open SQLite warehouse: {error}")

    st.info(
        "Expected database location: database/warehouse.db"
    )

    st.stop()


# =========================================================
# 4. WAREHOUSE RECORD COUNTS
# =========================================================

@st.cache_data
def get_warehouse_counts():

    query = """
        SELECT
            (SELECT COUNT(*) FROM dim_customer) AS customers,
            (SELECT COUNT(*) FROM dim_product) AS products,
            (SELECT COUNT(*) FROM dim_order) AS orders,
            (SELECT COUNT(*) FROM fact_sales) AS sales_records
    """

    return read_sqlite_query(query)


st.divider()

st.subheader("Warehouse Data Record Counts")

counts = get_warehouse_counts()

count1, count2, count3, count4 = st.columns(4)

count1.metric(
    "Customers",
    f"{int(counts.loc[0, 'customers']):,}"
)

count2.metric(
    "Products",
    f"{int(counts.loc[0, 'products']):,}"
)

count3.metric(
    "Orders",
    f"{int(counts.loc[0, 'orders']):,}"
)

count4.metric(
    "Sales Records",
    f"{int(counts.loc[0, 'sales_records']):,}"
)


# =========================================================
# 5. AVAILABLE DATE RANGE
# =========================================================

@st.cache_data
def get_available_dates():

    result = read_sqlite_query("""
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
# 6. DATE FILTER SECTION
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
# 7. LOAD FILTERED ANALYTICS FROM SQLITE
# =========================================================

@st.cache_data
def load_data(start_date, end_date):

    date_params = (
        str(start_date),
        str(end_date)
    )

    # -----------------------------------------------------
    # KPI QUERY
    # -----------------------------------------------------

    kpis = read_sqlite_query("""

        SELECT

            ROUND(
                COALESCE(SUM(f.net_amount), 0),
                2
            ) AS revenue,

            COUNT(
                DISTINCT f.order_id
            ) AS total_orders,

            ROUND(
                COALESCE(SUM(f.net_amount), 0) /
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

        WHERE d.full_date BETWEEN ? AND ?

    """, date_params)


    # -----------------------------------------------------
    # MONTHLY REVENUE QUERY
    # -----------------------------------------------------

    monthly = read_sqlite_query("""

        SELECT

            d.year AS year,

            d.month AS month,

            ROUND(
                SUM(f.net_amount),
                2
            ) AS revenue

        FROM fact_sales f

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE d.full_date BETWEEN ? AND ?

        GROUP BY
            d.year,
            d.month

        ORDER BY
            d.year,
            d.month

    """, date_params)


    # -----------------------------------------------------
    # REGION-WISE REVENUE QUERY
    # -----------------------------------------------------

    regional = read_sqlite_query("""

        SELECT

            c.region,

            ROUND(
                SUM(f.net_amount),
                2
            ) AS revenue

        FROM fact_sales f

        JOIN dim_customer c
            ON f.customer_key = c.customer_key

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE d.full_date BETWEEN ? AND ?

        GROUP BY c.region

        ORDER BY revenue DESC

    """, date_params)


    # -----------------------------------------------------
    # TOP 5 PRODUCTS QUERY
    # -----------------------------------------------------

    products = read_sqlite_query("""

        SELECT

            p.product_name,

            SUM(f.quantity) AS quantity_sold,

            ROUND(
                SUM(f.net_amount),
                2
            ) AS revenue

        FROM fact_sales f

        JOIN dim_product p
            ON f.product_key = p.product_key

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE d.full_date BETWEEN ? AND ?

        GROUP BY
            p.product_key,
            p.product_name

        ORDER BY revenue DESC

        LIMIT 5

    """, date_params)


    # -----------------------------------------------------
    # DETAILED SALES TRANSACTIONS
    # -----------------------------------------------------

    sales_details = read_sqlite_query("""

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

            f.gross_amount AS gross_sales,

            f.discount_amount,

            f.net_amount AS net_sales,

            o.order_status

        FROM fact_sales f

        JOIN dim_date d
            ON f.date_key = d.date_key

        JOIN dim_customer c
            ON f.customer_key = c.customer_key

        JOIN dim_product p
            ON f.product_key = p.product_key

        JOIN dim_order o
            ON f.order_key = o.order_key

        WHERE d.full_date BETWEEN ? AND ?

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
# 8. EXECUTE SQLITE ANALYTICS
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
        f"Unable to load analytics from SQLite: {error}"
    )

    st.stop()


# =========================================================
# 9. KPI CARDS
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
    "Total Orders",
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
# 10. MONTHLY REVENUE CHART
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
# 11. REGION AND PRODUCT CHARTS
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
# 12. SUMMARY TABLES
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
# 13. DETAILED SALES TRANSACTIONS
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
# 14. FOOTER
# =========================================================

st.divider()

st.caption(
    "Analytics source: SQLite Retail Data Warehouse | "
    "Reviewer Mode: Read-only | "
    "MySQL Server: Not Required"
)
