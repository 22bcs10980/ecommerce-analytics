"""
Enterprise E-Commerce Analytical Business Intelligence Layer.
Provides modular, reusable analytical functions for executive KPIs, sales trends,
product economics, customer lifetime value, cohort retention, and geographic performance.

Database: SQLite (data/processed/cleaned_ecommerce.db)
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any, Union

# Auto-detect project base directory and virtual environment
BASE_DIR = Path(__file__).resolve().parent.parent
VENV_SITE = BASE_DIR / ".venv" / "Lib" / "site-packages"
if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
    sys.path.insert(0, str(VENV_SITE))

DEFAULT_DB_PATH = BASE_DIR / "data" / "processed" / "cleaned_ecommerce.db"
DEFAULT_PROCESSED_DIR = BASE_DIR / "data" / "processed"


def get_db_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """
    Establish and return a connection to the SQLite database.
    
    Args:
        db_path: Path to the SQLite database file. Defaults to DEFAULT_DB_PATH.
        
    Returns:
        sqlite3.Connection object.
        
    Raises:
        FileNotFoundError: If the database file does not exist.
    """
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Database not found at '{path}'. Please run 'src/data_cleaning.py' first."
        )
    return sqlite3.connect(str(path))


def execute_query(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
    conn: Optional[sqlite3.Connection] = None,
    db_path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Safely execute a SQL query and return results as a Pandas DataFrame.
    
    Args:
        query: SQL query string.
        params: Optional tuple of query parameters.
        conn: Optional active database connection. If None, opens a new connection.
        db_path: Optional path to SQLite database if opening new connection.
        
    Returns:
        pd.DataFrame containing query results.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection(db_path)
        should_close = True
        
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    finally:
        if should_close:
            conn.close()


def load_clean_tables(processed_dir: Optional[Union[str, Path]] = None) -> Dict[str, pd.DataFrame]:
    """
    Load all 5 cleaned relational tables into a dictionary of DataFrames.
    
    Args:
        processed_dir: Directory containing cleaned CSV files.
        
    Returns:
        Dictionary mapping table name to DataFrame.
    """
    pdir = Path(processed_dir) if processed_dir else DEFAULT_PROCESSED_DIR
    tables = ['customers', 'products', 'orders', 'order_items', 'payments']
    dfs = {}
    
    for t in tables:
        csv_file = pdir / f"{t}_clean.csv"
        if csv_file.exists():
            dfs[t] = pd.read_csv(csv_file)
        else:
            dfs[t] = execute_query(f"SELECT * FROM {t};")
            
    return dfs


def get_executive_kpis(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """
    Calculate high-level realized executive and financial KPIs.
    
    Business Logic:
        Only realized commercial orders (order_status IN ('Delivered', 'Shipped'))
        are included for top-line revenue and bottom-line profit calculations.
        
    Returns:
        Dictionary of financial and operational KPI metrics.
    """
    query = """
        SELECT 
            SUM(oi.gross_revenue) AS gross_revenue,
            SUM(oi.discount_amount) AS total_discount,
            SUM(oi.net_revenue) AS net_revenue,
            SUM(oi.total_cost) AS total_cost,
            SUM(oi.profit) AS total_profit,
            COUNT(DISTINCT o.order_id) AS fulfilled_orders,
            COUNT(DISTINCT o.customer_id) AS active_customers,
            SUM(oi.quantity) AS total_units_sold
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status IN ('Delivered', 'Shipped');
    """
    df = execute_query(query, conn=conn)
    
    gross_rev = float(df['gross_revenue'].iloc[0] or 0.0)
    total_disc = float(df['total_discount'].iloc[0] or 0.0)
    net_rev = float(df['net_revenue'].iloc[0] or 0.0)
    total_cost = float(df['total_cost'].iloc[0] or 0.0)
    net_profit = float(df['total_profit'].iloc[0] or 0.0)
    fulfilled_orders = int(df['fulfilled_orders'].iloc[0] or 0)
    active_customers = int(df['active_customers'].iloc[0] or 0)
    units_sold = int(df['total_units_sold'].iloc[0] or 0)
    
    # Calculate Total Orders across all fulfillment statuses
    total_orders_df = execute_query("SELECT COUNT(*) AS total_orders FROM orders;", conn=conn)
    total_orders_all = int(total_orders_df['total_orders'].iloc[0] or 0)
    
    # Calculate Derived Ratios
    aov = net_rev / fulfilled_orders if fulfilled_orders > 0 else 0.0
    profit_margin_pct = (net_profit / net_rev * 100.0) if net_rev > 0 else 0.0
    effective_discount_rate_pct = (total_disc / gross_rev * 100.0) if gross_rev > 0 else 0.0
    avg_units_per_order = units_sold / fulfilled_orders if fulfilled_orders > 0 else 0.0
    
    # Repeat Purchase Rate
    rpr_query = """
        WITH cust_orders AS (
            SELECT customer_id, COUNT(order_id) AS cnt
            FROM orders
            WHERE order_status IN ('Delivered', 'Shipped')
            GROUP BY customer_id
        )
        SELECT 
            COUNT(customer_id) AS total_active_custs,
            SUM(CASE WHEN cnt > 1 THEN 1 ELSE 0 END) AS repeat_custs
        FROM cust_orders;
    """
    rpr_df = execute_query(rpr_query, conn=conn)
    tot_active_c = int(rpr_df['total_active_custs'].iloc[0] or 0)
    repeat_c = int(rpr_df['repeat_custs'].iloc[0] or 0)
    repeat_purchase_rate_pct = (repeat_c / tot_active_c * 100.0) if tot_active_c > 0 else 0.0
    
    return {
        'total_gross_revenue': round(gross_rev, 2),
        'total_discount_amount': round(total_disc, 2),
        'total_realized_revenue': round(net_rev, 2),
        'total_product_cost': round(total_cost, 2),
        'total_realized_profit': round(net_profit, 2),
        'overall_profit_margin_pct': round(profit_margin_pct, 2),
        'effective_discount_rate_pct': round(effective_discount_rate_pct, 2),
        'total_orders_all': total_orders_all,
        'fulfilled_orders_count': fulfilled_orders,
        'fulfillment_rate_pct': round(fulfilled_orders / total_orders_all * 100.0, 2) if total_orders_all > 0 else 0.0,
        'active_customers_count': active_customers,
        'average_order_value_aov': round(aov, 2),
        'average_units_per_order': round(avg_units_per_order, 2),
        'repeat_customers_count': repeat_c,
        'repeat_purchase_rate_pct': round(repeat_purchase_rate_pct, 2)
    }


def get_monthly_revenue_trend(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Aggregate monthly realized revenue, profit, margin %, order counts, and units sold.
    
    Returns:
        pd.DataFrame with monthly time-series metrics.
    """
    query = """
        SELECT 
            SUBSTR(o.order_date, 1, 7) AS order_month,
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS active_customers,
            SUM(oi.quantity) AS total_units_sold,
            ROUND(SUM(oi.gross_revenue), 2) AS gross_revenue,
            ROUND(SUM(oi.discount_amount), 2) AS total_discounts,
            ROUND(SUM(oi.net_revenue), 2) AS net_revenue,
            ROUND(SUM(oi.total_cost), 2) AS total_cost,
            ROUND(SUM(oi.profit), 2) AS net_profit,
            ROUND((SUM(oi.profit) * 100.0 / SUM(oi.net_revenue)), 2) AS profit_margin_pct,
            ROUND(SUM(oi.net_revenue) / COUNT(DISTINCT o.order_id), 2) AS monthly_aov
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status IN ('Delivered', 'Shipped')
        GROUP BY SUBSTR(o.order_date, 1, 7)
        ORDER BY order_month ASC;
    """
    df = execute_query(query, conn=conn)
    df['order_date_dt'] = pd.to_datetime(df['order_month'])
    return df


def get_yoy_growth_trend(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Calculate Year-over-Year (YoY) revenue dollar and percentage growth rates.
    
    Returns:
        pd.DataFrame comparing current year vs prior year monthly revenue.
    """
    query = """
        WITH monthly_sales AS (
            SELECT 
                CAST(SUBSTR(o.order_date, 1, 4) AS INT) AS order_year,
                CAST(SUBSTR(o.order_date, 6, 2) AS INT) AS order_month_num,
                SUBSTR(o.order_date, 1, 7) AS year_month,
                ROUND(SUM(oi.net_revenue), 2) AS net_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY order_year, order_month_num, year_month
        ),
        yoy_growth AS (
            SELECT 
                year_month,
                order_year,
                order_month_num,
                net_revenue AS current_year_revenue,
                LAG(net_revenue, 1) OVER (
                    PARTITION BY order_month_num 
                    ORDER BY order_year ASC
                ) AS prior_year_revenue
            FROM monthly_sales
        )
        SELECT 
            year_month,
            current_year_revenue,
            prior_year_revenue,
            ROUND(current_year_revenue - prior_year_revenue, 2) AS revenue_yoy_dollar_change,
            CASE 
                WHEN prior_year_revenue IS NULL OR prior_year_revenue = 0 THEN NULL
                ELSE ROUND(((current_year_revenue - prior_year_revenue) * 100.0 / prior_year_revenue), 2)
            END AS yoy_growth_rate_pct
        FROM yoy_growth
        ORDER BY year_month ASC;
    """
    return execute_query(query, conn=conn)


def get_category_performance(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Analyze revenue, profit, margin %, and cumulative Pareto contribution by category.
    
    Returns:
        pd.DataFrame with category performance metrics and cumulative Pareto %.
    """
    query = """
        WITH category_totals AS (
            SELECT 
                p.category,
                COUNT(DISTINCT oi.order_id) AS order_count,
                SUM(oi.quantity) AS total_units_sold,
                ROUND(SUM(oi.net_revenue), 2) AS category_revenue,
                ROUND(SUM(oi.profit), 2) AS category_profit,
                ROUND((SUM(oi.profit) * 100.0 / SUM(oi.net_revenue)), 2) AS profit_margin_pct
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY p.category
        ),
        category_pareto AS (
            SELECT 
                category,
                order_count,
                total_units_sold,
                category_revenue,
                category_profit,
                profit_margin_pct,
                ROUND(category_revenue * 100.0 / SUM(category_revenue) OVER (), 2) AS revenue_share_pct,
                ROUND(SUM(category_revenue) OVER (
                    ORDER BY category_revenue DESC 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) * 100.0 / SUM(category_revenue) OVER (), 2) AS cumulative_pareto_revenue_pct
            FROM category_totals
        )
        SELECT * FROM category_pareto
        ORDER BY category_revenue DESC;
    """
    return execute_query(query, conn=conn)


def get_product_performance(
    top_n: int = 20,
    conn: Optional[sqlite3.Connection] = None
) -> pd.DataFrame:
    """
    Return top-performing products ranked by net revenue.

    Parameters
    ----------
    top_n : int
        Number of products to return.
    conn : sqlite3.Connection, optional
        Existing database connection.

    Returns
    -------
    pd.DataFrame
        Product performance metrics.
    """

    if conn is None:
        conn = get_connection()

    top_n = int(top_n)

    query = f"""
        WITH ranked_prods AS (
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                p.sub_category,

                SUM(oi.quantity) AS total_units_sold,

                ROUND(
                    SUM(oi.net_revenue),
                    2
                ) AS total_net_revenue,

                ROUND(
                    SUM(oi.profit),
                    2
                ) AS total_profit,

                ROUND(
                    (
                        SUM(oi.profit) * 100.0
                        / NULLIF(SUM(oi.net_revenue), 0)
                    ),
                    2
                ) AS profit_margin_pct,

                DENSE_RANK() OVER (
                    ORDER BY SUM(oi.net_revenue) DESC
                ) AS rank_pos

            FROM products p

            JOIN order_items oi
                ON p.product_id = oi.product_id

            JOIN orders o
                ON oi.order_id = o.order_id

            WHERE o.order_status IN (
                'Delivered',
                'Shipped'
            )

            GROUP BY
                p.product_id,
                p.product_name,
                p.category,
                p.sub_category
        )

        SELECT
            rank_pos,
            product_id,
            product_name,
            category,
            sub_category,
            total_units_sold,
            total_net_revenue,
            total_profit,
            profit_margin_pct

        FROM ranked_prods

        WHERE rank_pos <= {top_n}

        ORDER BY rank_pos ASC;
    """

    return execute_query(
        query,
        conn=conn
    )
def get_declining_products(
    limit: int = 15,
    conn: Optional[sqlite3.Connection] = None
) -> pd.DataFrame:
    """
    Identify products experiencing consecutive quarterly sales declines.
    
    Returns:
        pd.DataFrame of products with largest quarterly revenue drop.
    """
    query = f"""
        WITH product_quarterly_sales AS (
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                SUBSTR(o.order_date, 1, 4) || '-Q' || ((CAST(SUBSTR(o.order_date, 6, 2) AS INT) - 1) / 3 + 1) AS sales_quarter,
                SUM(oi.net_revenue) AS quarter_revenue
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY p.product_id, p.product_name, p.category, sales_quarter
        ),
        quarterly_comparison AS (
            SELECT 
                product_id,
                product_name,
                category,
                sales_quarter,
                quarter_revenue,
                LAG(quarter_revenue, 1) OVER (
                    PARTITION BY product_id 
                    ORDER BY sales_quarter ASC
                ) AS prev_quarter_revenue
            FROM product_quarterly_sales
        )
        SELECT 
            product_id,
            product_name,
            category,
            sales_quarter,
            ROUND(quarter_revenue, 2) AS current_quarter_rev,
            ROUND(prev_quarter_revenue, 2) AS prior_quarter_rev,
            ROUND(quarter_revenue - prev_quarter_revenue, 2) AS revenue_decline_amount,
            ROUND(((quarter_revenue - prev_quarter_revenue) * 100.0 / prev_quarter_revenue), 2) AS decline_pct
        FROM quarterly_comparison
        WHERE prev_quarter_revenue IS NOT NULL 
          AND quarter_revenue < prev_quarter_revenue
        ORDER BY revenue_decline_amount ASC
        LIMIT {limit};
    """
    return execute_query(query, conn=conn)


def get_discount_tier_analysis(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Evaluate revenue, units sold, profit, and effective margin % across promotional discount tiers.
    
    Returns:
        pd.DataFrame of discount tiers with volume and margin metrics.
    """
    query = """
        SELECT 
            CASE 
                WHEN discount_rate = 0.0 THEN '0% (Full Price)'
                WHEN discount_rate > 0.0 AND discount_rate <= 0.10 THEN '1% - 10% (Low Discount)'
                WHEN discount_rate > 0.10 AND discount_rate <= 0.20 THEN '11% - 20% (Medium Discount)'
                WHEN discount_rate > 0.20 THEN '21%+ (Heavy Promo)'
                ELSE 'Other'
            END AS discount_tier,
            COUNT(order_item_id) AS line_item_count,
            SUM(quantity) AS total_units_sold,
            ROUND(SUM(gross_revenue), 2) AS total_gross_revenue,
            ROUND(SUM(discount_amount), 2) AS total_discount_amount,
            ROUND(SUM(net_revenue), 2) AS total_net_revenue,
            ROUND(SUM(profit), 2) AS total_profit,
            ROUND((SUM(profit) * 100.0 / SUM(net_revenue)), 2) AS effective_profit_margin_pct
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status IN ('Delivered', 'Shipped')
        GROUP BY discount_tier
        ORDER BY total_net_revenue DESC;
    """
    return execute_query(query, conn=conn)


def get_geographic_performance(
    level: str = 'state',
    limit: int = 50,
    conn: Optional[sqlite3.Connection] = None
) -> pd.DataFrame:
    """
    Analyze sales volume, revenue, profit, and AOV across geographic regions.
    
    Args:
        level: 'state' or 'city'.
        limit: Max rows returned.
        conn: Optional active database connection.
        
    Returns:
        pd.DataFrame with regional performance metrics.
    """
    if level == 'city':
        query = f"""
            SELECT 
                c.city,
                c.state,
                COUNT(DISTINCT o.order_id) AS total_orders,
                COUNT(DISTINCT c.customer_id) AS unique_customers,
                ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
                ROUND(SUM(oi.profit), 2) AS total_profit,
                ROUND(SUM(oi.net_revenue) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY c.city, c.state
            ORDER BY total_net_revenue DESC
            LIMIT {limit};
        """
    else:
        query = f"""
            SELECT 
                c.state,
                COUNT(DISTINCT o.order_id) AS total_orders,
                COUNT(DISTINCT c.customer_id) AS unique_customers,
                ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
                ROUND(SUM(oi.profit), 2) AS total_profit,
                ROUND(SUM(oi.net_revenue) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY c.state
            ORDER BY total_net_revenue DESC
            LIMIT {limit};
        """
    return execute_query(query, conn=conn)


def get_clv_by_segment(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Calculate Customer Lifetime Value (CLV), average orders, and profit per segment.
    
    Returns:
        pd.DataFrame of CLV metrics grouped by customer_segment.
    """
    query = """
        WITH customer_financials AS (
            SELECT 
                c.customer_id,
                c.customer_segment,
                COUNT(DISTINCT o.order_id) AS total_orders,
                SUM(oi.net_revenue) AS total_lifetime_revenue,
                SUM(oi.profit) AS total_lifetime_profit
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY c.customer_id, c.customer_segment
        )
        SELECT 
            customer_segment,
            COUNT(customer_id) AS total_customers,
            ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
            ROUND(AVG(total_lifetime_revenue), 2) AS avg_customer_lifetime_value_clv,
            ROUND(AVG(total_lifetime_profit), 2) AS avg_customer_lifetime_profit,
            ROUND(SUM(total_lifetime_revenue), 2) AS total_segment_revenue
        FROM customer_financials
        GROUP BY customer_segment
        ORDER BY avg_customer_lifetime_value_clv DESC;
    """
    return execute_query(query, conn=conn)


def get_new_vs_returning_trend(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Track monthly orders and revenue split between new vs returning customers.
    
    Returns:
        pd.DataFrame with new vs returning monthly dynamics.
    """
    query = """
        WITH customer_first_order AS (
            SELECT 
                customer_id,
                SUBSTR(MIN(order_date), 1, 7) AS first_order_month
            FROM orders
            WHERE order_status IN ('Delivered', 'Shipped')
            GROUP BY customer_id
        ),
        order_classification AS (
            SELECT 
                o.order_id,
                o.customer_id,
                SUBSTR(o.order_date, 1, 7) AS order_month,
                SUM(oi.net_revenue) AS order_revenue,
                CASE 
                    WHEN SUBSTR(o.order_date, 1, 7) = cfo.first_order_month THEN 'New Customer'
                    ELSE 'Returning Customer'
                END AS customer_type
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN customer_first_order cfo ON o.customer_id = cfo.customer_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY o.order_id, o.customer_id, o.order_date, cfo.first_order_month
        )
        SELECT 
            order_month,
            SUM(CASE WHEN customer_type = 'New Customer' THEN 1 ELSE 0 END) AS new_customer_orders,
            SUM(CASE WHEN customer_type = 'Returning Customer' THEN 1 ELSE 0 END) AS returning_customer_orders,
            ROUND(SUM(CASE WHEN customer_type = 'New Customer' THEN order_revenue ELSE 0 END), 2) AS new_customer_revenue,
            ROUND(SUM(CASE WHEN customer_type = 'Returning Customer' THEN order_revenue ELSE 0 END), 2) AS returning_customer_revenue,
            ROUND(SUM(CASE WHEN customer_type = 'Returning Customer' THEN order_revenue ELSE 0 END) * 100.0 / SUM(order_revenue), 2) AS returning_revenue_share_pct
        FROM order_classification
        GROUP BY order_month
        ORDER BY order_month ASC;
    """
    return execute_query(query, conn=conn)


def get_monthly_active_customers(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Calculate Monthly Active Customers (MAC / MAU) and order velocity per customer.
    
    Returns:
        pd.DataFrame with monthly active customer metrics.
    """
    query = """
        SELECT 
            SUBSTR(o.order_date, 1, 7) AS active_month,
            COUNT(DISTINCT o.customer_id) AS monthly_active_customers,
            COUNT(DISTINCT o.order_id) AS total_monthly_orders,
            ROUND(COUNT(DISTINCT o.order_id) * 1.0 / COUNT(DISTINCT o.customer_id), 2) AS orders_per_active_customer,
            ROUND(SUM(oi.net_revenue) / COUNT(DISTINCT o.customer_id), 2) AS revenue_per_active_customer
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status IN ('Delivered', 'Shipped')
        GROUP BY SUBSTR(o.order_date, 1, 7)
        ORDER BY active_month ASC;
    """
    return execute_query(query, conn=conn)


def get_cohort_matrix(
    max_months: int = 12,
    conn: Optional[sqlite3.Connection] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate customer cohort counts and percentage retention matrix.
    
    Args:
        max_months: Maximum tracking months (M+0 to M+max_months).
        conn: Optional active database connection.
        
    Returns:
        Tuple of (cohort_counts_df, cohort_retention_pct_df).
    """
    query = f"""
        WITH customer_cohort AS (
            SELECT 
                customer_id,
                SUBSTR(MIN(order_date), 1, 7) AS cohort_month
            FROM orders
            WHERE order_status IN ('Delivered', 'Shipped')
            GROUP BY customer_id
        ),
        user_activities AS (
            SELECT 
                o.customer_id,
                cc.cohort_month,
                (CAST(SUBSTR(o.order_date, 1, 4) AS INT) - CAST(SUBSTR(cc.cohort_month, 1, 4) AS INT)) * 12 +
                (CAST(SUBSTR(o.order_date, 6, 2) AS INT) - CAST(SUBSTR(cc.cohort_month, 6, 2) AS INT)) AS month_number
            FROM orders o
            JOIN customer_cohort cc ON o.customer_id = cc.customer_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY o.customer_id, cc.cohort_month, month_number
        ),
        cohort_size AS (
            SELECT 
                cohort_month,
                COUNT(DISTINCT customer_id) AS total_cohort_size
            FROM customer_cohort
            GROUP BY cohort_month
        )
        SELECT 
            ua.cohort_month,
            cs.total_cohort_size,
            ua.month_number,
            COUNT(DISTINCT ua.customer_id) AS active_users
        FROM user_activities ua
        JOIN cohort_size cs ON ua.cohort_month = cs.cohort_month
        WHERE ua.month_number <= {max_months}
        GROUP BY ua.cohort_month, cs.total_cohort_size, ua.month_number
        ORDER BY ua.cohort_month ASC, ua.month_number ASC;
    """
    df = execute_query(query, conn=conn)
    cohort_counts = df.pivot(index='cohort_month', columns='month_number', values='active_users')
    cohort_sizes = df.groupby('cohort_month')['total_cohort_size'].first()
    cohort_retention_pct = (cohort_counts.divide(cohort_sizes, axis=0) * 100.0).round(1)
    
    return cohort_counts, cohort_retention_pct


def get_decile_concentration(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """
    Compute customer spend deciles (NTILE(10)) to analyze revenue concentration.
    
    Returns:
        pd.DataFrame of spend deciles with revenue contribution percentages.
    """
    query = """
        WITH customer_spend AS (
            SELECT 
                c.customer_id,
                SUM(oi.net_revenue) AS total_customer_spend
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY c.customer_id
        ),
        deciles AS (
            SELECT 
                customer_id,
                total_customer_spend,
                NTILE(10) OVER (ORDER BY total_customer_spend ASC) AS spend_decile
            FROM customer_spend
        )
        SELECT 
            spend_decile,
            COUNT(customer_id) AS customer_count,
            ROUND(MIN(total_customer_spend), 2) AS min_spend_in_decile,
            ROUND(MAX(total_customer_spend), 2) AS max_spend_in_decile,
            ROUND(SUM(total_customer_spend), 2) AS total_decile_revenue,
            ROUND(SUM(total_customer_spend) * 100.0 / (SELECT SUM(total_customer_spend) FROM customer_spend), 2) AS decile_revenue_share_pct
        FROM deciles
        GROUP BY spend_decile
        ORDER BY spend_decile DESC;
    """
    return execute_query(query, conn=conn)


def get_churn_risk_customers(
    min_days_inactive: int = 90,
    min_historic_orders: int = 2,
    limit: int = 50,
    conn: Optional[sqlite3.Connection] = None
) -> pd.DataFrame:
    """
    Identify dormant repeat customers representing immediate churn revenue exposure.
    
    Returns:
        pd.DataFrame of at-risk customer accounts.
    """
    query = f"""
        WITH customer_inactivity AS (
            SELECT 
                c.customer_id,
                c.customer_name,
                c.email,
                c.city,
                c.state,
                c.customer_segment,
                MAX(o.order_date) AS last_order_date,
                CAST(JULIANDAY('2026-06-30') - JULIANDAY(MAX(o.order_date)) AS INT) AS days_inactive,
                COUNT(DISTINCT o.order_id) AS historic_orders,
                ROUND(SUM(oi.net_revenue), 2) AS historic_lifetime_spend
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status IN ('Delivered', 'Shipped')
            GROUP BY c.customer_id, c.customer_name, c.email, c.city, c.state, c.customer_segment
        )
        SELECT 
            customer_id,
            customer_name,
            email,
            city,
            state,
            customer_segment,
            historic_orders,
            historic_lifetime_spend,
            last_order_date,
            days_inactive,
            CASE 
                WHEN days_inactive >= 270 THEN 'Severe Churn Risk (9+ Months Inactive)'
                WHEN days_inactive >= 180 THEN 'High Churn Risk (6-9 Months Inactive)'
                WHEN days_inactive >= 90 THEN 'Moderate Churn Risk (3-6 Months Inactive)'
                ELSE 'Active'
            END AS churn_risk_tier
        FROM customer_inactivity
        WHERE days_inactive >= {min_days_inactive} AND historic_orders >= {min_historic_orders}
        ORDER BY historic_lifetime_spend DESC
        LIMIT {limit};
    """
    return execute_query(query, conn=conn)


if __name__ == '__main__':
    print("Testing src/analysis.py module...")
    kpis = get_executive_kpis()
    print("Executive KPIs Summary:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")