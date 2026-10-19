"""
dashboard/app.py
────────────────
Streamlit dashboard for the Retail Sales ETL project.

Run with:
    streamlit run dashboard/app.py

Requires a .env file (or environment variables) with Snowflake credentials.
The ANALYTICS views must already exist in Snowflake (run sql/02_analytics_views.sql).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Allow imports from project root when running from the dashboard/ directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import get_snowflake_config  # noqa: E402

# ── Page configuration ────────────────────────────────────
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="🛒",
    layout="wide",
)


# ── Snowflake connection (cached) ─────────────────────────
@st.cache_resource(show_spinner="Connecting to Snowflake …")
def get_connection():
    import snowflake.connector

    cfg = get_snowflake_config()
    return snowflake.connector.connect(
        account=cfg.account,
        user=cfg.user,
        password=cfg.password,
        database=cfg.database,
        warehouse=cfg.warehouse,
        schema="ANALYTICS",
        role=cfg.role,
    )


@st.cache_data(ttl=300, show_spinner="Running query …")
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


# ── KPI helpers ───────────────────────────────────────────
def fmt_currency(value: float) -> str:
    """Format a BRL value with thousands separator."""
    return f"R$ {value:,.0f}"


# ── Layout ────────────────────────────────────────────────
st.title("🛒 Retail Sales Analytics")
st.caption(
    "Olist Brazilian E-Commerce · values in Brazilian reais (BRL) · "
    "data refreshes every 5 minutes"
)

# ── KPI row ───────────────────────────────────────────────
with st.spinner("Loading KPIs …"):
    kpi_df = run_query(
        """
        SELECT
            SUM(order_count)   AS total_orders,
            SUM(total_price)   AS total_price,
            SUM(total_freight) AS total_freight,
            SUM(total_revenue) AS total_revenue
        FROM RETAIL_SALES.ANALYTICS.VW_DAILY_SALES
        """
    )
    pay_df = run_query(
        """
        SELECT SUM(total_payment_value) AS total_payments
        FROM RETAIL_SALES.ANALYTICS.VW_PAYMENT_SUMMARY
        """
    )

kpi = kpi_df.iloc[0]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders",       f"{int(kpi['TOTAL_ORDERS']):,}")
k2.metric("Item Revenue (BRL)", fmt_currency(kpi["TOTAL_PRICE"]))
k3.metric("Freight (BRL)",      fmt_currency(kpi["TOTAL_FREIGHT"]))
k4.metric("Payment Value (BRL)", fmt_currency(pay_df.iloc[0]["TOTAL_PAYMENTS"]))

st.divider()

# ── Row 1: Daily sales trend ──────────────────────────────
st.subheader("Daily Sales Trend")
daily_df = run_query(
    """
    SELECT
        SALE_DATE,
        ORDER_COUNT,
        TOTAL_REVENUE
    FROM RETAIL_SALES.ANALYTICS.VW_DAILY_SALES
    ORDER BY SALE_DATE
    """
)
daily_df["SALE_DATE"] = pd.to_datetime(daily_df["SALE_DATE"])
fig_daily = px.line(
    daily_df,
    x="SALE_DATE",
    y="TOTAL_REVENUE",
    labels={"SALE_DATE": "Date", "TOTAL_REVENUE": "Revenue (BRL)"},
    template="plotly_white",
)
fig_daily.update_traces(line_color="#3b82d4")
st.plotly_chart(fig_daily, use_container_width=True)

st.divider()

# ── Row 2: Category revenue + Order status ────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Product Categories")
    cat_df = run_query(
        """
        SELECT CATEGORY, TOTAL_REVENUE
        FROM RETAIL_SALES.ANALYTICS.VW_CATEGORY_REVENUE
        LIMIT 10
        """
    )
    fig_cat = px.bar(
        cat_df,
        x="TOTAL_REVENUE",
        y="CATEGORY",
        orientation="h",
        labels={"TOTAL_REVENUE": "Revenue (BRL)", "CATEGORY": "Category"},
        template="plotly_white",
        color_discrete_sequence=["#3b82d4"],
    )
    fig_cat.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    st.subheader("Order Status Distribution")
    status_df = run_query(
        """
        SELECT ORDER_STATUS, ORDER_COUNT
        FROM RETAIL_SALES.ANALYTICS.VW_ORDER_STATUS
        """
    )
    fig_status = px.pie(
        status_df,
        names="ORDER_STATUS",
        values="ORDER_COUNT",
        template="plotly_white",
        hole=0.4,
    )
    st.plotly_chart(fig_status, use_container_width=True)

st.divider()

# ── Row 3: Payment method breakdown ──────────────────────
st.subheader("Payment Methods")
pay_type_df = run_query(
    """
    SELECT PAYMENT_TYPE, TOTAL_PAYMENT_VALUE, ORDER_COUNT
    FROM RETAIL_SALES.ANALYTICS.VW_PAYMENT_SUMMARY
    """
)
fig_pay = px.bar(
    pay_type_df,
    x="PAYMENT_TYPE",
    y="TOTAL_PAYMENT_VALUE",
    labels={"PAYMENT_TYPE": "Method", "TOTAL_PAYMENT_VALUE": "Total Value (BRL)"},
    template="plotly_white",
    color_discrete_sequence=["#7c5cd8"],
    text_auto=".2s",
)
st.plotly_chart(fig_pay, use_container_width=True)

st.caption("Made with IBM Bob · Retail Sales ETL Snowflake Project")
