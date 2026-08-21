import os
import sys
import sqlite3
import streamlit as st
import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "cleaned_ecommerce.db"
)

SRC_PATH = os.path.join(
    BASE_DIR,
    "src"
)

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


# =========================================================
# IMPORT ANALYTICS MODULES
# =========================================================

from analysis import (
    get_executive_kpis,
    get_monthly_revenue_trend,
    get_yoy_growth_trend,
    get_category_performance,
    get_product_performance,
    get_geographic_performance,
    get_clv_by_segment,
    get_new_vs_returning_trend,
    get_churn_risk_customers
)

from rfm import compute_rfm_segmentation
from forecasting import generate_sales_forecast


# =========================================================
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(
    page_title="E-Commerce Business Intelligence",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_resource
def get_connection():

    if not os.path.exists(DB_PATH):
        st.error(
            f"Database not found: {DB_PATH}"
        )
        st.stop()

    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )


conn = get_connection()


# =========================================================
# HEADER
# =========================================================

st.title(
    "📊 E-Commerce Business Intelligence Platform"
)

st.caption(
    "Executive analytics • Customer intelligence • "
    "Sales performance • Forecasting"
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "📊 E-Commerce BI"
)

st.sidebar.markdown(
    "## Business Intelligence Platform"
)

st.sidebar.caption(
    "Analytics dashboard for revenue, customers, "
    "products, geography and forecasting."
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Sales Analytics",
        "Customer Analytics",
        "Product Analytics",
        "Geographic Analytics",
        "Forecasting"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Data source: SQLite"
)

st.sidebar.caption(
    "Analytics: Python • Pandas"
)

st.sidebar.caption(
    "Dashboard: Streamlit"
)


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================

if page == "Executive Overview":

    st.header(
        "📊 Executive Overview"
    )

    st.caption(
        "Key business performance indicators at a glance"
    )

    try:

        kpis = get_executive_kpis(
            conn
        )

        # -------------------------------------------------
        # FINANCIAL PERFORMANCE
        # -------------------------------------------------

        st.subheader(
            "💰 Financial Performance"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Realized Revenue",
            f"₹{kpis['total_realized_revenue']:,.2f}"
        )

        col2.metric(
            "Realized Profit",
            f"₹{kpis['total_realized_profit']:,.2f}"
        )

        col3.metric(
            "Profit Margin",
            f"{kpis['overall_profit_margin_pct']:.2f}%"
        )

        st.divider()

        # -------------------------------------------------
        # ORDERS & CUSTOMERS
        # -------------------------------------------------

        st.subheader(
            "🛒 Orders & Customers"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Orders",
            f"{kpis['total_orders_all']:,}"
        )

        col2.metric(
            "Active Customers",
            f"{kpis['active_customers_count']:,}"
        )

        col3.metric(
            "Average Order Value",
            f"₹{kpis['average_order_value_aov']:,.2f}"
        )

        col4.metric(
            "Average Units / Order",
            f"{kpis['average_units_per_order']:.2f}"
        )

        st.divider()

        # -------------------------------------------------
        # CUSTOMER & FULFILLMENT
        # -------------------------------------------------

        st.subheader(
            "📦 Customer & Fulfillment"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Fulfillment Rate",
            f"{kpis['fulfillment_rate_pct']:.2f}%"
        )

        col2.metric(
            "Repeat Purchase Rate",
            f"{kpis['repeat_purchase_rate_pct']:.2f}%"
        )

        col3.metric(
            "Fulfilled Orders",
            f"{kpis['fulfilled_orders_count']:,}"
        )

        st.divider()

        # -------------------------------------------------
        # QUICK BUSINESS INSIGHTS
        # -------------------------------------------------

        st.subheader(
            "💡 Quick Business Insights"
        )

        insight1, insight2, insight3 = st.columns(3)

        insight1.info(
            f"💰 The business generated "
            f"₹{kpis['total_realized_revenue']:,.0f} "
            f"in realized revenue."
        )

        insight2.info(
            f"📦 {kpis['fulfillment_rate_pct']:.2f}% "
            f"of orders were fulfilled."
        )

        insight3.info(
            f"🔄 {kpis['repeat_purchase_rate_pct']:.2f}% "
            f"of customers made repeat purchases."
        )

    except Exception as e:

        st.error(
            f"Unable to load KPI data: {e}"
        )


# =========================================================
# SALES ANALYTICS
# =========================================================

elif page == "Sales Analytics":

    st.header(
        "📈 Sales Analytics"
    )

    st.caption(
        "Track revenue performance and year-over-year growth"
    )

    try:

        # -------------------------------------------------
        # MONTHLY REVENUE TREND
        # -------------------------------------------------

        st.subheader(
            "💰 Monthly Revenue Trend"
        )

        monthly = get_monthly_revenue_trend(
            conn=conn
        )

        chart_data = monthly[
            [
                "order_month",
                "net_revenue"
            ]
        ].copy()

        chart_data["order_month"] = pd.to_datetime(
            chart_data["order_month"]
        )

        chart_data = chart_data.set_index(
            "order_month"
        )

        st.line_chart(
            chart_data["net_revenue"],
            width="stretch"
        )

        # -------------------------------------------------
        # MONTHLY SALES PERFORMANCE
        # -------------------------------------------------

        st.subheader(
            "📋 Monthly Sales Performance"
        )

        display_columns = [
            "order_month",
            "total_orders",
            "active_customers",
            "total_units_sold",
            "gross_revenue",
            "total_discounts",
            "net_revenue",
            "total_cost",
            "net_profit",
            "profit_margin_pct",
            "monthly_aov"
        ]

        available_columns = [
            column
            for column in display_columns
            if column in monthly.columns
        ]

        st.dataframe(
            monthly[available_columns],
            width="stretch",
            hide_index=True
        )

        st.divider()

        # -------------------------------------------------
        # YEAR-OVER-YEAR GROWTH
        # -------------------------------------------------

        st.subheader(
            "📊 Year-over-Year Growth"
        )

        yoy = get_yoy_growth_trend(
            conn=conn
        )

        if (
            not yoy.empty
            and "yoy_growth_rate_pct" in yoy.columns
        ):

            yoy_chart = yoy[
                [
                    "year_month",
                    "yoy_growth_rate_pct"
                ]
            ].copy()

            yoy_chart["year_month"] = pd.to_datetime(
                yoy_chart["year_month"]
            )

            yoy_chart = yoy_chart.dropna(
                subset=[
                    "yoy_growth_rate_pct"
                ]
            )

            yoy_chart = yoy_chart.set_index(
                "year_month"
            )

            st.line_chart(
                yoy_chart[
                    "yoy_growth_rate_pct"
                ],
                width="stretch"
            )

            st.caption(
                "Year-over-year revenue growth rate (%)"
            )

            st.dataframe(
                yoy,
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                "Year-over-year growth data "
                "is not available yet."
            )

    except Exception as e:

        st.error(
            f"Unable to load sales analytics: {e}"
        )


# =========================================================
# CUSTOMER ANALYTICS
# =========================================================

elif page == "Customer Analytics":

    st.header(
        "👥 Customer Analytics"
    )

    st.caption(
        "Customer segmentation, lifetime value and churn analysis"
    )

    try:

        customer_rfm, segment_summary = (
            compute_rfm_segmentation(
                conn=conn
            )
        )

        # -------------------------------------------------
        # RFM SEGMENTS
        # -------------------------------------------------

        st.subheader(
            "RFM Customer Segments"
        )

        st.dataframe(
            segment_summary,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # CUSTOMER DISTRIBUTION
        # -------------------------------------------------

        st.subheader(
            "Customer Distribution"
        )

        if (
            not segment_summary.empty
            and "rfm_segment" in segment_summary.columns
            and "customer_count" in segment_summary.columns
        ):

            customer_chart = segment_summary[
                [
                    "rfm_segment",
                    "customer_count"
                ]
            ].set_index(
                "rfm_segment"
            )

            st.bar_chart(
                customer_chart,
                width="stretch"
            )

        # -------------------------------------------------
        # CUSTOMER LIFETIME VALUE
        # -------------------------------------------------

        st.subheader(
            "Customer Lifetime Value"
        )

        clv = get_clv_by_segment(
            conn=conn
        )

        st.dataframe(
            clv,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # NEW VS RETURNING
        # -------------------------------------------------

        st.subheader(
            "New vs Returning Customers"
        )

        returning = get_new_vs_returning_trend(
            conn=conn
        )

        st.dataframe(
            returning,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # CHURN RISK
        # -------------------------------------------------

        st.subheader(
            "Churn Risk Customers"
        )

        churn = get_churn_risk_customers(
            conn=conn
        )

        st.dataframe(
            churn,
            width="stretch",
            hide_index=True
        )

    except Exception as e:

        st.error(
            f"Unable to load customer analytics: {e}"
        )


# =========================================================
# PRODUCT ANALYTICS
# =========================================================

elif page == "Product Analytics":

    st.header(
        "🏆 Product Analytics"
    )

    st.caption(
        "Category and product performance analysis"
    )

    try:

        # -------------------------------------------------
        # CATEGORY PERFORMANCE
        # -------------------------------------------------

        categories = get_category_performance(
            conn=conn
        )

        st.subheader(
            "Category Performance"
        )

        st.dataframe(
            categories,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # REVENUE BY CATEGORY
        # -------------------------------------------------

        if (
            not categories.empty
            and "category" in categories.columns
            and "category_revenue" in categories.columns
        ):

            st.subheader(
                "📊 Revenue by Category"
            )

            category_chart = categories[
                [
                    "category",
                    "category_revenue"
                ]
            ].copy()

            category_chart = category_chart.set_index(
                "category"
            )

            st.bar_chart(
                category_chart,
                width="stretch"
            )

        st.divider()

        # -------------------------------------------------
        # PRODUCT PERFORMANCE
        # -------------------------------------------------

        products = get_product_performance(
            conn=conn
        )

        st.subheader(
            "Product Performance"
        )

        st.dataframe(
            products,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # TOP PRODUCTS
        # -------------------------------------------------

        if (
            not products.empty
            and "product_name" in products.columns
            and "total_net_revenue" in products.columns
        ):

            st.subheader(
                "🏆 Top Products by Revenue"
            )

            top_products = products[
                [
                    "product_name",
                    "total_net_revenue"
                ]
            ].copy()

            top_products = top_products.sort_values(
                "total_net_revenue",
                ascending=False
            ).head(10)

            top_products = top_products.set_index(
                "product_name"
            )

            st.bar_chart(
                top_products,
                width="stretch"
            )

    except Exception as e:

        st.error(
            f"Unable to load product analytics: {e}"
        )


# =========================================================
# GEOGRAPHIC ANALYTICS
# =========================================================

elif page == "Geographic Analytics":

    st.header(
        "🌍 Geographic Analytics"
    )

    st.caption(
        "Analyze business performance across geographic regions"
    )

    try:

        geographic = get_geographic_performance(
            conn=conn
        )

        # -------------------------------------------------
        # STATE PERFORMANCE
        # -------------------------------------------------

        st.subheader(
            "State Performance"
        )

        st.dataframe(
            geographic,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # REVENUE BY STATE
        # -------------------------------------------------

        if (
            not geographic.empty
            and "state" in geographic.columns
            and "total_net_revenue" in geographic.columns
        ):

            st.subheader(
                "💰 Revenue by State"
            )

            state_chart = geographic[
                [
                    "state",
                    "total_net_revenue"
                ]
            ].copy()

            state_chart = state_chart.sort_values(
                "total_net_revenue",
                ascending=False
            )

            state_chart = state_chart.set_index(
                "state"
            )

            st.bar_chart(
                state_chart,
                width="stretch"
            )

        # -------------------------------------------------
        # PROFIT BY STATE
        # -------------------------------------------------

        if (
            not geographic.empty
            and "state" in geographic.columns
            and "total_profit" in geographic.columns
        ):

            st.subheader(
                "💵 Profit by State"
            )

            profit_chart = geographic[
                [
                    "state",
                    "total_profit"
                ]
            ].copy()

            profit_chart = profit_chart.sort_values(
                "total_profit",
                ascending=False
            )

            profit_chart = profit_chart.set_index(
                "state"
            )

            st.bar_chart(
                profit_chart,
                width="stretch"
            )

    except Exception as e:

        st.error(
            f"Unable to load geographic analytics: {e}"
        )


# =========================================================
# FORECASTING
# =========================================================

elif page == "Forecasting":

    st.header(
        "🔮 Sales Forecasting"
    )

    st.caption(
        "Historical revenue and future sales projections"
    )

    try:

        historical, forecast = (
            generate_sales_forecast(
                conn=conn,
                forecast_months=6
            )
        )

        # -------------------------------------------------
        # HISTORICAL REVENUE
        # -------------------------------------------------

        st.subheader(
            "Historical Revenue"
        )

        st.dataframe(
            historical,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # NEXT 6 MONTHS FORECAST
        # -------------------------------------------------

        st.subheader(
            "Next 6 Months Forecast"
        )

        st.dataframe(
            forecast,
            width="stretch",
            hide_index=True
        )

        # -------------------------------------------------
        # FORECAST CHART
        # -------------------------------------------------

        if (
            not forecast.empty
            and len(forecast.columns) >= 2
        ):

            st.subheader(
                "📈 Forecast Trend"
            )

            forecast_chart = forecast.copy()

            date_column = forecast_chart.columns[0]
            value_column = forecast_chart.columns[1]

            forecast_chart[date_column] = pd.to_datetime(
                forecast_chart[date_column],
                errors="coerce"
            )

            forecast_chart[value_column] = pd.to_numeric(
                forecast_chart[value_column],
                errors="coerce"
            )

            forecast_chart = forecast_chart.dropna(
                subset=[
                    date_column,
                    value_column
                ]
            )

            if not forecast_chart.empty:

                forecast_chart = forecast_chart.set_index(
                    date_column
                )

                st.line_chart(
                    forecast_chart[value_column],
                    width="stretch"
                )

    except Exception as e:

        st.error(
            f"Unable to load forecast: {e}"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "E-Commerce Business Intelligence Platform | "
    "Python • SQLite • Pandas • Streamlit"
)