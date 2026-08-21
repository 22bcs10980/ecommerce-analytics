-- ============================================================================
-- 02_SALES_AND_PRODUCT_ANALYTICS.SQL
-- Product Performance, Category Dynamics, Geography & Pricing Strategy
-- Queries: 8, 9, 10, 11, 12, 13, 18, 19, 20
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 8: Top 10 Products by Revenue (Using DENSE_RANK())
-- Business Question: Which top 10 catalog items contribute the highest net sales volume?
-- Purpose: Merchandising priority, inventory allocation, and flagship product monitoring.
-- ----------------------------------------------------------------------------
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
        DENSE_RANK() OVER (ORDER BY SUM(oi.net_revenue) DESC) AS revenue_rank
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY p.product_id, p.product_name, p.category, p.sub_category
)
SELECT 
    revenue_rank,
    product_id,
    product_name,
    category,
    sub_category,
    total_units_sold,
    total_net_revenue
FROM product_sales
WHERE revenue_rank <= 10
ORDER BY revenue_rank ASC;


-- ----------------------------------------------------------------------------
-- Query 9: Top 10 Products by Profit and Margin
-- Business Question: Which top 10 products generate the highest cumulative gross profit dollar value?
-- Purpose: Profit driver analysis and marketing budget prioritization.
-- ----------------------------------------------------------------------------
WITH product_profit AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
        ROUND(SUM(oi.profit), 2) AS total_profit,
        ROUND((SUM(oi.profit) * 100.0 / SUM(oi.net_revenue)), 2) AS profit_margin_pct,
        DENSE_RANK() OVER (ORDER BY SUM(oi.profit) DESC) AS profit_rank
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT 
    profit_rank,
    product_id,
    product_name,
    category,
    total_net_revenue,
    total_profit,
    profit_margin_pct
FROM product_profit
WHERE profit_rank <= 10
ORDER BY profit_rank ASC;


-- ----------------------------------------------------------------------------
-- Query 10: Best-Performing Product Categories
-- Business Question: What are the revenue, profit, and margin contributions of each product category?
-- Purpose: Portfolio management and category management strategy.
-- ----------------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS order_count,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
    ROUND(SUM(oi.profit), 2) AS total_profit,
    ROUND((SUM(oi.profit) * 100.0 / SUM(oi.net_revenue)), 2) AS profit_margin_pct
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY p.category
ORDER BY total_net_revenue DESC;


-- ----------------------------------------------------------------------------
-- Query 11: Worst-Performing Categories / Loss Centers
-- Business Question: Which categories or sub-categories generate the lowest profit margins?
-- Purpose: Identify product lines requiring supplier renegotiation or rationalization.
-- ----------------------------------------------------------------------------
SELECT 
    p.category,
    p.sub_category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
    ROUND(SUM(oi.profit), 2) AS total_profit,
    ROUND((SUM(oi.profit) * 100.0 / SUM(oi.net_revenue)), 2) AS profit_margin_pct,
    ROUND(AVG(oi.discount_rate) * 100.0, 2) AS avg_discount_pct
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY p.category, p.sub_category
ORDER BY total_profit ASC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- Query 12: Revenue by State / Region
-- Business Question: How is realized customer revenue distributed geographically across US states?
-- Purpose: Regional marketing spend targeting and supply chain warehouse optimization.
-- ----------------------------------------------------------------------------
SELECT 
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_id) AS unique_customers,
    ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
    ROUND(SUM(oi.profit), 2) AS total_profit,
    ROUND(SUM(oi.net_revenue) / COUNT(DISTINCT o.order_id), 2) AS state_avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY c.state
ORDER BY total_net_revenue DESC;


-- ----------------------------------------------------------------------------
-- Query 13: Revenue by Top 20 Cities
-- Business Question: Which top 20 metropolitan cities drive the largest share of commercial revenue?
-- Purpose: Hyper-local ad targeting and metropolitan distribution hub selection.
-- ----------------------------------------------------------------------------
SELECT 
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(DISTINCT c.customer_id) AS customer_count,
    ROUND(SUM(oi.net_revenue), 2) AS total_net_revenue,
    ROUND(SUM(oi.profit), 2) AS total_profit
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY c.city, c.state
ORDER BY total_net_revenue DESC
LIMIT 20;


-- ----------------------------------------------------------------------------
-- Query 18: Products with Declining Sales using Window Functions
-- Business Question: Which products experienced consecutive quarterly revenue decline?
-- Purpose: Early warning churn signal for catalog items losing consumer demand.
-- ----------------------------------------------------------------------------
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
LIMIT 15;


-- ----------------------------------------------------------------------------
-- Query 19: Discount vs Profit Analysis
-- Business Question: How do promotional discount tiers affect sales volume and margin erosion?
-- Purpose: Establish discount ceilings to protect profit margins.
-- ----------------------------------------------------------------------------
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


-- ----------------------------------------------------------------------------
-- Query 20: Revenue Contribution by Category and Cumulative Pareto %
-- Business Question: What is the individual and cumulative Pareto revenue share of each product category?
-- Purpose: Apply the 80/20 rule to determine core revenue-generating business pillars.
-- ----------------------------------------------------------------------------
WITH category_totals AS (
    SELECT 
        p.category,
        ROUND(SUM(oi.net_revenue), 2) AS category_revenue,
        ROUND(SUM(oi.profit), 2) AS category_profit
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY p.category
),
category_pareto AS (
    SELECT 
        category,
        category_revenue,
        category_profit,
        ROUND(category_revenue * 100.0 / SUM(category_revenue) OVER (), 2) AS pct_of_total_revenue,
        ROUND(SUM(category_revenue) OVER (ORDER BY category_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) * 100.0 / SUM(category_revenue) OVER (), 2) AS cumulative_pareto_revenue_pct
    FROM category_totals
)
SELECT 
    category,
    category_revenue,
    category_profit,
    pct_of_total_revenue,
    cumulative_pareto_revenue_pct
FROM category_pareto
ORDER BY category_revenue DESC;