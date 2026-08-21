"""
E-Commerce Sales Forecasting Engine.
Provides monthly sales trends, moving averages, and linear trend forecasts.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from typing import Optional, Tuple


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

venv_site = os.path.join(BASE_DIR, '.venv', 'Lib', 'site-packages')

if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)


DB_PATH = os.path.join(
    BASE_DIR,
    'data',
    'processed',
    'cleaned_ecommerce.db'
)


def generate_sales_forecast(
    conn: Optional[sqlite3.Connection] = None,
    forecast_months: int = 6
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    should_close = False

    if conn is None:

        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(
                f"Database missing at {DB_PATH}"
            )

        conn = sqlite3.connect(DB_PATH)
        should_close = True

    query = """
        SELECT
            strftime('%Y-%m', o.order_date) AS month,
            ROUND(SUM(oi.net_revenue), 2) AS revenue,
            ROUND(SUM(oi.profit), 2) AS profit,
            COUNT(DISTINCT o.order_id) AS orders
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE o.order_status IN ('Delivered', 'Shipped')
        GROUP BY strftime('%Y-%m', o.order_date)
        ORDER BY month;
    """

    df = pd.read_sql_query(query, conn)

    if should_close:
        conn.close()

    if df.empty:
        raise ValueError(
            "No sales data available for forecasting."
        )

    df['month'] = pd.to_datetime(df['month'])

    df['revenue'] = pd.to_numeric(df['revenue'])
    df['profit'] = pd.to_numeric(df['profit'])
    df['orders'] = pd.to_numeric(df['orders'])

    # 3-month moving averages

    df['revenue_ma_3'] = (
        df['revenue']
        .rolling(window=3, min_periods=1)
        .mean()
        .round(2)
    )

    df['profit_ma_3'] = (
        df['profit']
        .rolling(window=3, min_periods=1)
        .mean()
        .round(2)
    )

    # Linear trend forecasting

    x = np.arange(len(df))

    revenue_model = np.polyfit(
        x,
        df['revenue'],
        1
    )

    profit_model = np.polyfit(
        x,
        df['profit'],
        1
    )

    future_x = np.arange(
        len(df),
        len(df) + forecast_months
    )

    future_dates = pd.date_range(
        start=df['month'].iloc[-1] + pd.offsets.MonthBegin(1),
        periods=forecast_months,
        freq='MS'
    )

    forecast = pd.DataFrame({
        'month': future_dates,

        'forecast_revenue': np.polyval(
            revenue_model,
            future_x
        ).round(2),

        'forecast_profit': np.polyval(
            profit_model,
            future_x
        ).round(2)
    })

    # Prevent negative forecasts

    forecast['forecast_revenue'] = (
        forecast['forecast_revenue']
        .clip(lower=0)
    )

    forecast['forecast_profit'] = (
        forecast['forecast_profit']
        .clip(lower=0)
    )

    return df, forecast


if __name__ == '__main__':

    historical, forecast = generate_sales_forecast(
        forecast_months=6
    )

    print("Historical Monthly Sales:")
    print(historical.to_string(index=False))

    print("\n6-Month Sales Forecast:")
    print(forecast.to_string(index=False))