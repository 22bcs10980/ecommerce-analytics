"""
RFM Customer Segmentation & Customer Lifetime Value (CLV) Engine
Computes Recency, Frequency, Monetary (RFM) distributions, behavioral personas,
and customer retention metrics.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site = os.path.join(BASE_DIR, '.venv', 'Lib', 'site-packages')
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

DB_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_ecommerce.db')

def compute_rfm_segmentation(
    conn: Optional[sqlite3.Connection] = None,
    reference_date: str = '2026-06-30'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute customer RFM scores (1 to 5) and assign strategic behavioral segments.
    Returns:
    - customer_level_rfm: DataFrame with each customer's R, F, M, scores, and segment.
    - segment_summary: Aggregated DataFrame summarizing size, revenue, and averages by segment.
    """
    should_close = False
    if conn is None:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database missing at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        should_close = True

    # Pull customer transaction metrics
    query = f"""
        SELECT 
            c.customer_id,
            c.customer_name,
            c.email,
            c.city,
            c.state,
            c.customer_segment,
            c.signup_date,
            MAX(o.order_date) AS last_order_date,
            MIN(o.order_date) AS first_order_date,
            COUNT(DISTINCT o.order_id) AS frequency,
            ROUND(SUM(oi.net_revenue), 2) AS monetary_value,
            ROUND(SUM(oi.profit), 2) AS total_profit,
            SUM(oi.quantity) AS total_units_purchased
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status IN ('Delivered', 'Shipped')
        GROUP BY c.customer_id, c.customer_name, c.email, c.city, c.state, c.customer_segment, c.signup_date;
    """
    df = pd.read_sql_query(query, conn)
    if should_close:
        conn.close()

    ref_dt = pd.to_datetime(reference_date)
    df['last_order_date'] = pd.to_datetime(df['last_order_date'])
    df['first_order_date'] = pd.to_datetime(df['first_order_date'])
    df['recency_days'] = (ref_dt - df['last_order_date']).dt.days.clip(lower=0)

    # 5-Tier Quantile Scoring
    # Recency: Lower days = better score (5 is best)
    df['r_score'] = pd.qcut(df['recency_days'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    
    # Frequency: Higher count = better score (ranking with method='first' for clean binning)
    df['f_score'] = pd.qcut(df['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Monetary: Higher spend = better score
    df['m_score'] = pd.qcut(df['monetary_value'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    df['rfm_score_combo'] = df['r_score'].astype(str) + df['f_score'].astype(str) + df['m_score'].astype(str)
    df['rfm_composite_index'] = (df['r_score'] * 0.20 + df['f_score'] * 0.30 + df['m_score'] * 0.50).round(2)

    # Strategic Segment Mapping
    def assign_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'Recent Customers'
        elif r >= 3 and f <= 2 and m >= 3:
            return 'Promising'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r == 1 and f >= 4:
            return "Can't Lose Them"
        elif r <= 2 and f <= 2:
            return 'Hibernating / Lost'
        else:
            return 'Need Attention'

    df['rfm_segment'] = df.apply(assign_segment, axis=1)

    # Segment Summary Table
    total_rev = df['monetary_value'].sum()
    summary = df.groupby('rfm_segment').agg(
        customer_count=('customer_id', 'count'),
        avg_recency_days=('recency_days', 'mean'),
        avg_frequency=('frequency', 'mean'),
        avg_monetary_spend=('monetary_value', 'mean'),
        avg_profit=('total_profit', 'mean'),
        total_revenue=('monetary_value', 'sum'),
        total_profit=('total_profit', 'sum')
    ).reset_index()

    summary['avg_recency_days'] = summary['avg_recency_days'].round(1)
    summary['avg_frequency'] = summary['avg_frequency'].round(2)
    summary['avg_monetary_spend'] = summary['avg_monetary_spend'].round(2)
    summary['avg_profit'] = summary['avg_profit'].round(2)
    summary['total_revenue'] = summary['total_revenue'].round(2)
    summary['total_profit'] = summary['total_profit'].round(2)
    summary['revenue_share_pct'] = (summary['total_revenue'] * 100.0 / total_rev).round(2)
    summary['customer_share_pct'] = (summary['customer_count'] * 100.0 / len(df)).round(2)

    summary = summary.sort_values(by='total_revenue', ascending=False).reset_index(drop=True)
    return df, summary

if __name__ == '__main__':
    cust_rfm, summary = compute_rfm_segmentation()
    print(f"RFM Segment Summary (Total Customers: {len(cust_rfm):,}):")
    print(summary.to_string())