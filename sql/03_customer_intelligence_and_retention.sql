-- ============================================================================
-- 03_CUSTOMER_INTELLIGENCE_AND_RETENTION.SQL
-- Customer Behavior, Retention, RFM Segmentation & Churn Risk
-- Queries: 14, 15, 16, 17, 21, 22, 23, 24, 25
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 14: New vs Returning Customers by Month
-- Business Question: What proportion of monthly sales comes from new vs returning shoppers?
-- Purpose: Measure reliance on customer acquisition vs organic retention.
-- ----------------------------------------------------------------------------
WITH customer_first_order AS (
    SELECT 
        customer_id,
        MIN(order_date) AS first_order_date,
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


-- ----------------------------------------------------------------------------
-- Query 15: Repeat Purchase Rate (RPR)
-- Business Question: What percentage of unique acquired customers place multiple orders?
-- Purpose: Core customer stickiness and product-market fit indicator.
-- ----------------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(order_id) AS total_orders
    FROM orders
    WHERE order_status IN ('Delivered', 'Shipped')
    GROUP BY customer_id
)
SELECT 
    COUNT(customer_id) AS total_active_customers,
    SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END) AS single_order_customers,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id), 2) AS repeat_purchase_rate_pct
FROM customer_order_counts;


-- ----------------------------------------------------------------------------
-- Query 16: Average Customer Lifetime Value (CLV)
-- Business Question: What is the average realized Lifetime Value and Profit per customer segment?
-- Purpose: Establish Customer Acquisition Cost (CAC) thresholds and segment targeting.
-- ----------------------------------------------------------------------------
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
    ROUND(AVG(total_lifetime_profit), 2) AS avg_customer_lifetime_profit
FROM customer_financials
GROUP BY customer_segment
ORDER BY avg_customer_lifetime_value_clv DESC;


-- ----------------------------------------------------------------------------
-- Query 17: Top Spending Customers (VIPs)
-- Business Question: Who are the top 20 highest-spending VIP accounts on the platform?
-- Purpose: Concierge account management, loyalty rewards, and VIP retention.
-- ----------------------------------------------------------------------------
WITH customer_spend AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.city,
        c.state,
        c.customer_segment,
        COUNT(DISTINCT o.order_id) AS completed_orders,
        SUM(oi.quantity) AS total_items_purchased,
        ROUND(SUM(oi.net_revenue), 2) AS total_net_spend,
        ROUND(SUM(oi.profit), 2) AS total_profit_generated,
        DENSE_RANK() OVER (ORDER BY SUM(oi.net_revenue) DESC) AS spend_rank
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, c.customer_name, c.city, c.state, c.customer_segment
)
SELECT 
    spend_rank,
    customer_id,
    customer_name,
    city,
    state,
    customer_segment,
    completed_orders,
    total_items_purchased,
    total_net_spend,
    total_profit_generated
FROM customer_spend
WHERE spend_rank <= 20
ORDER BY spend_rank ASC;


-- ----------------------------------------------------------------------------
-- Query 21: Monthly Active Customers (MAC / MAU)
-- Business Question: How many distinct active customers transacted each month?
-- Purpose: Monitor platform monthly active user retention and transaction velocity.
-- ----------------------------------------------------------------------------
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


-- ----------------------------------------------------------------------------
-- Query 22: Customer Cohort Retention Matrix
-- Business Question: What percentage of newly acquired users return in subsequent months (M+0 to M+6)?
-- Purpose: Measure long-term platform stickiness and cohort decay curves.
-- ----------------------------------------------------------------------------
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
    COUNT(DISTINCT ua.customer_id) AS active_users,
    ROUND(COUNT(DISTINCT ua.customer_id) * 100.0 / cs.total_cohort_size, 2) AS retention_rate_pct
FROM user_activities ua
JOIN cohort_size cs ON ua.cohort_month = cs.cohort_month
WHERE ua.month_number <= 6
GROUP BY ua.cohort_month, cs.total_cohort_size, ua.month_number
ORDER BY ua.cohort_month ASC, ua.month_number ASC;


-- ----------------------------------------------------------------------------
-- Query 23: RFM Customer Segmentation (NTILE Scoring)
-- Business Question: How are customers grouped into actionable behavioral personas
-- using Recency, Frequency, and Monetary scores?
-- Purpose: Precision email marketing, loyalty incentives, and retention campaigns.
-- ----------------------------------------------------------------------------
WITH rfm_raw AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.email,
        c.city,
        c.state,
        MAX(o.order_date) AS last_order_date,
        CAST(JULIANDAY('2026-06-30') - JULIANDAY(MAX(o.order_date)) AS INT) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.net_revenue), 2) AS monetary_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, c.customer_name, c.email, c.city, c.state
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        email,
        city,
        state,
        recency_days,
        frequency,
        monetary_value,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM rfm_raw
),
rfm_segmented AS (
    SELECT 
        customer_id,
        customer_name,
        email,
        city,
        state,
        recency_days,
        frequency,
        monetary_value,
        r_score,
        f_score,
        m_score,
        (r_score || f_score || m_score) AS rfm_combined,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Customers'
            WHEN r_score >= 3 AND f_score <= 2 AND m_score >= 3 THEN 'Promising'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk Customers'
            WHEN r_score = 1 AND f_score >= 4 THEN 'Can’t Lose Them'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating / Lost'
            ELSE 'Need Attention'
        END AS rfm_segment
    FROM rfm_scores
)
SELECT 
    rfm_segment,
    COUNT(customer_id) AS customer_count,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 2) AS avg_orders,
    ROUND(AVG(monetary_value), 2) AS avg_monetary_spend,
    ROUND(SUM(monetary_value), 2) AS total_segment_revenue,
    ROUND(SUM(monetary_value) * 100.0 / (SELECT SUM(net_revenue) FROM order_items oi JOIN orders o ON oi.order_id=o.order_id WHERE o.order_status IN ('Delivered','Shipped')), 2) AS pct_revenue_contribution
FROM rfm_segmented
GROUP BY rfm_segment
ORDER BY total_segment_revenue DESC;


-- ----------------------------------------------------------------------------
-- Query 24: Top 10% Decile Customer Contribution to Revenue (NTILE(10))
-- Business Question: What percentage of total revenue is concentrated in the top 10% of spenders?
-- Purpose: Validate Pareto 80/20 revenue concentration risks.
-- ----------------------------------------------------------------------------
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


-- ----------------------------------------------------------------------------
-- Query 25: Churn Risk Detection (Inactive > 90 / 180 Days with Repeat Order History)
-- Business Question: Which previously active repeat customers have stopped buying and are at risk of churning?
-- Purpose: Win-back marketing and reactivation discount trigger lists.
-- ----------------------------------------------------------------------------
WITH customer_inactivity AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.email,
        c.city,
        c.state,
        MAX(o.order_date) AS last_order_date,
        CAST(JULIANDAY('2026-06-30') - JULIANDAY(MAX(o.order_date)) AS INT) AS days_inactive,
        COUNT(DISTINCT o.order_id) AS historic_orders,
        ROUND(SUM(oi.net_revenue), 2) AS historic_lifetime_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, c.customer_name, c.email, c.city, c.state
)
SELECT 
    customer_id,
    customer_name,
    email,
    city,
    state,
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
WHERE days_inactive >= 90 AND historic_orders >= 2
ORDER BY historic_lifetime_spend DESC
LIMIT 25;