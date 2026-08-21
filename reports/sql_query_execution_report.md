# SQL Analytical Suite Execution & Validation Report

**Execution Timestamp:** 2026-08-19 18:48:45

**Database:** `C:\Users\HP\.gemini\antigravity\scratch\ecommerce-analytics\data\processed\cleaned_ecommerce.db`

## 1. Summary of Execution Results

| # | Query Name | Category | Status | Rows Returned | Latency (ms) |
| :-: | :--- | :--- | :-: | :-: | :-: |
| 1 | **Total Realized Revenue** | Executive KPIs | `SUCCESS` | 1 | 54.10 |
| 2 | **Total Realized Profit & Margin** | Executive KPIs | `SUCCESS` | 1 | 47.13 |
| 3 | **Total Orders & Order Status Breakdown** | Executive KPIs | `SUCCESS` | 5 | 12.45 |
| 4 | **Average Order Value (AOV)** | Executive KPIs | `SUCCESS` | 1 | 67.65 |
| 5 | **Monthly Revenue Trend** | Executive KPIs | `SUCCESS` | 34 | 105.58 |
| 6 | **Monthly Profit and Profit Margin Trend** | Executive KPIs | `SUCCESS` | 34 | 78.31 |
| 7 | **Year-over-Year (YoY) Revenue Growth using LAG()** | Executive KPIs | `SUCCESS` | 34 | 88.39 |
| 8 | **Top 10 Products by Revenue (Using DENSE_RANK())** | Sales & Product Analytics | `SUCCESS` | 10 | 143.22 |
| 9 | **Top 10 Products by Profit and Margin** | Sales & Product Analytics | `SUCCESS` | 10 | 135.61 |
| 10 | **Best-Performing Product Categories** | Sales & Product Analytics | `SUCCESS` | 5 | 124.26 |
| 11 | **Worst-Performing Categories / Loss Centers** | Sales & Product Analytics | `SUCCESS` | 10 | 138.04 |
| 12 | **Revenue by State / Region** | Sales & Product Analytics | `SUCCESS` | 31 | 115.83 |
| 13 | **Revenue by Top 20 Cities** | Sales & Product Analytics | `SUCCESS` | 20 | 124.06 |
| 14 | **New vs Returning Customers by Month** | Customer Intelligence & Retention | `SUCCESS` | 34 | 188.26 |
| 15 | **Repeat Purchase Rate (RPR)** | Customer Intelligence & Retention | `SUCCESS` | 1 | 25.69 |
| 16 | **Average Customer Lifetime Value (CLV)** | Customer Intelligence & Retention | `SUCCESS` | 3 | 126.39 |
| 17 | **Top Spending Customers (VIPs)** | Customer Intelligence & Retention | `SUCCESS` | 20 | 232.05 |
| 18 | **Products with Declining Sales using Window Functions** | Sales & Product Analytics | `SUCCESS` | 15 | 186.16 |
| 19 | **Discount vs Profit Analysis** | Sales & Product Analytics | `SUCCESS` | 4 | 86.37 |
| 20 | **Revenue Contribution by Category and Cumulative Pareto %** | Sales & Product Analytics | `SUCCESS` | 5 | 90.92 |
| 21 | **Monthly Active Customers (MAC / MAU)** | Customer Intelligence & Retention | `SUCCESS` | 34 | 110.46 |
| 22 | **Customer Cohort Retention Matrix** | Customer Intelligence & Retention | `SUCCESS` | 189 | 104.10 |
| 23 | **RFM Customer Segmentation (NTILE Scoring)** | Customer Intelligence & Retention | `SUCCESS` | 8 | 290.45 |
| 24 | **Top 10% Decile Customer Contribution to Revenue (NTILE(10))** | Customer Intelligence & Retention | `SUCCESS` | 10 | 92.46 |
| 25 | **Churn Risk Detection (Inactive > 90 / 180 Days with Repeat Order History)** | Customer Intelligence & Retention | `SUCCESS` | 25 | 181.31 |

## 2. Query Output Samples & Key Insights

### Query 1: Total Realized Revenue

- **Category**: Executive KPIs
- **Rows Returned**: 1
- **Columns**: `['total_gross_revenue', 'total_discount_given', 'total_realized_revenue', 'effective_discount_rate_pct']`

```json
[
  {
    "total_gross_revenue": 14411297.42,
    "total_discount_given": 1014236.85,
    "total_realized_revenue": 13397060.57,
    "effective_discount_rate_pct": 7.04
  }
]
```

### Query 2: Total Realized Profit & Margin

- **Category**: Executive KPIs
- **Rows Returned**: 1
- **Columns**: `['total_net_revenue', 'total_product_cost', 'total_realized_profit', 'overall_profit_margin_pct']`

```json
[
  {
    "total_net_revenue": 13397060.57,
    "total_product_cost": 5659285.15,
    "total_realized_profit": 7737775.42,
    "overall_profit_margin_pct": 57.76
  }
]
```

### Query 3: Total Orders & Order Status Breakdown

- **Category**: Executive KPIs
- **Rows Returned**: 5
- **Columns**: `['order_status', 'total_orders', 'pct_of_total_orders']`

```json
[
  {
    "order_status": "Delivered",
    "total_orders": 22294,
    "pct_of_total_orders": 85.75
  },
  {
    "order_status": "Shipped",
    "total_orders": 1361,
    "pct_of_total_orders": 5.23
  },
  {
    "order_status": "Cancelled",
    "total_orders": 1066,
    "pct_of_total_orders": 4.1
  }
]
```

### Query 4: Average Order Value (AOV)

- **Category**: Executive KPIs
- **Rows Returned**: 1
- **Columns**: `['fulfilled_order_count', 'average_order_value_aov', 'average_units_per_order']`

```json
[
  {
    "fulfilled_order_count": 23655,
    "average_order_value_aov": 566.35,
    "average_units_per_order": 2.62
  }
]
```

### Query 5: Monthly Revenue Trend

- **Category**: Executive KPIs
- **Rows Returned**: 34
- **Columns**: `['order_month', 'monthly_orders', 'total_units_sold', 'monthly_gross_revenue', 'monthly_discounts', 'monthly_net_revenue']`

```json
[
  {
    "order_month": "2024-01",
    "monthly_orders": 358,
    "total_units_sold": 935,
    "monthly_gross_revenue": 183736.8,
    "monthly_discounts": 10749.1,
    "monthly_net_revenue": 172987.7
  },
  {
    "order_month": "2024-02",
    "monthly_orders": 408,
    "total_units_sold": 1047,
    "monthly_gross_revenue": 272524.04,
    "monthly_discounts": 17709.4,
    "monthly_net_revenue": 254814.64
  },
  {
    "order_month": "2024-03",
    "monthly_orders": 448,
    "total_units_sold": 1159,
    "monthly_gross_revenue": 232732.28,
    "monthly_discounts": 16939.85,
    "monthly_net_revenue": 215792.43
  }
]
```

### Query 6: Monthly Profit and Profit Margin Trend

- **Category**: Executive KPIs
- **Rows Returned**: 34
- **Columns**: `['order_month', 'monthly_net_revenue', 'monthly_cost', 'monthly_net_profit', 'monthly_profit_margin_pct']`

```json
[
  {
    "order_month": "2024-01",
    "monthly_net_revenue": 172987.7,
    "monthly_cost": 69321.85,
    "monthly_net_profit": 103665.85,
    "monthly_profit_margin_pct": 59.93
  },
  {
    "order_month": "2024-02",
    "monthly_net_revenue": 254814.64,
    "monthly_cost": 110296.9,
    "monthly_net_profit": 144517.74,
    "monthly_profit_margin_pct": 56.71
  },
  {
    "order_month": "2024-03",
    "monthly_net_revenue": 215792.43,
    "monthly_cost": 89263.0,
    "monthly_net_profit": 126529.43,
    "monthly_profit_margin_pct": 58.63
  }
]
```

### Query 7: Year-over-Year (YoY) Revenue Growth using LAG()

- **Category**: Executive KPIs
- **Rows Returned**: 34
- **Columns**: `['year_month', 'current_year_revenue', 'prior_year_revenue', 'revenue_yoy_dollar_change', 'yoy_growth_rate_pct']`

```json
[
  {
    "year_month": "2024-01",
    "current_year_revenue": 172987.7,
    "prior_year_revenue": NaN,
    "revenue_yoy_dollar_change": NaN,
    "yoy_growth_rate_pct": NaN
  },
  {
    "year_month": "2024-02",
    "current_year_revenue": 254814.64,
    "prior_year_revenue": NaN,
    "revenue_yoy_dollar_change": NaN,
    "yoy_growth_rate_pct": NaN
  },
  {
    "year_month": "2024-03",
    "current_year_revenue": 215792.43,
    "prior_year_revenue": NaN,
    "revenue_yoy_dollar_change": NaN,
    "yoy_growth_rate_pct": NaN
  }
]
```

### Query 8: Top 10 Products by Revenue (Using DENSE_RANK())

- **Category**: Sales & Product Analytics
- **Rows Returned**: 10
- **Columns**: `['revenue_rank', 'product_id', 'product_name', 'category', 'sub_category', 'total_units_sold', 'total_net_revenue']`

```json
[
  {
    "revenue_rank": 1,
    "product_id": "PROD-1042",
    "product_name": "Pro Gaming Laptop 16-inch - Pro Edition",
    "category": "Electronics",
    "sub_category": "Laptops & Computers",
    "total_units_sold": 134,
    "total_net_revenue": 256351.69
  },
  {
    "revenue_rank": 2,
    "product_id": "PROD-1048",
    "product_name": "Pro Gaming Laptop 16-inch - Special Bundle",
    "category": "Electronics",
    "sub_category": "Laptops & Computers",
    "total_units_sold": 118,
    "total_net_revenue": 250947.06
  },
  {
    "revenue_rank": 3,
    "product_id": "PROD-1043",
    "product_name": "Pro Gaming Laptop 16-inch - Plus",
    "category": "Electronics",
    "sub_category": "Laptops & Computers",
    "total_units_sold": 123,
    "total_net_revenue": 215569.24
  }
]
```

### Query 9: Top 10 Products by Profit and Margin

- **Category**: Sales & Product Analytics
- **Rows Returned**: 10
- **Columns**: `['profit_rank', 'product_id', 'product_name', 'category', 'total_net_revenue', 'total_profit', 'profit_margin_pct']`

```json
[
  {
    "profit_rank": 1,
    "product_id": "PROD-1042",
    "product_name": "Pro Gaming Laptop 16-inch - Pro Edition",
    "category": "Electronics",
    "total_net_revenue": 256351.69,
    "total_profit": 125701.69,
    "profit_margin_pct": 49.03
  },
  {
    "profit_rank": 2,
    "product_id": "PROD-1048",
    "product_name": "Pro Gaming Laptop 16-inch - Special Bundle",
    "category": "Electronics",
    "total_net_revenue": 250947.06,
    "total_profit": 117489.06,
    "profit_margin_pct": 46.82
  },
  {
    "profit_rank": 3,
    "product_id": "PROD-1043",
    "product_name": "Pro Gaming Laptop 16-inch - Plus",
    "category": "Electronics",
    "total_net_revenue": 215569.24,
    "total_profit": 105238.24,
    "profit_margin_pct": 48.82
  }
]
```

### Query 10: Best-Performing Product Categories

- **Category**: Sales & Product Analytics
- **Rows Returned**: 5
- **Columns**: `['category', 'order_count', 'total_units_sold', 'total_net_revenue', 'total_profit', 'profit_margin_pct']`

```json
[
  {
    "category": "Electronics",
    "order_count": 9805,
    "total_units_sold": 17667,
    "total_net_revenue": 7838191.48,
    "total_profit": 4063443.78,
    "profit_margin_pct": 51.84
  },
  {
    "category": "Home & Kitchen",
    "order_count": 8284,
    "total_units_sold": 14448,
    "total_net_revenue": 2594965.58,
    "total_profit": 1666649.53,
    "profit_margin_pct": 64.23
  },
  {
    "category": "Apparel & Fashion",
    "order_count": 8335,
    "total_units_sold": 14477,
    "total_net_revenue": 1521533.78,
    "total_profit": 1058183.58,
    "profit_margin_pct": 69.55
  }
]
```

### Query 11: Worst-Performing Categories / Loss Centers

- **Category**: Sales & Product Analytics
- **Rows Returned**: 10
- **Columns**: `['category', 'sub_category', 'units_sold', 'total_net_revenue', 'total_profit', 'profit_margin_pct', 'avg_discount_pct']`

```json
[
  {
    "category": "Electronics",
    "sub_category": "General Electronics",
    "units_sold": 107,
    "total_net_revenue": 17819.45,
    "total_profit": 10864.45,
    "profit_margin_pct": 60.97,
    "avg_discount_pct": 6.28
  },
  {
    "category": "Apparel & Fashion",
    "sub_category": "General Apparel & Fashion",
    "units_sold": 99,
    "total_net_revenue": 23337.6,
    "total_profit": 15912.6,
    "profit_margin_pct": 68.18,
    "avg_discount_pct": 4.85
  },
  {
    "category": "Beauty & Personal Care",
    "sub_category": "Skincare",
    "units_sold": 3668,
    "total_net_revenue": 121310.25,
    "total_profit": 87998.15,
    "profit_margin_pct": 72.54,
    "avg_discount_pct": 6.68
  }
]
```

### Query 12: Revenue by State / Region

- **Category**: Sales & Product Analytics
- **Rows Returned**: 31
- **Columns**: `['state', 'total_orders', 'unique_customers', 'total_net_revenue', 'total_profit', 'state_avg_order_value']`

```json
[
  {
    "state": "OH",
    "total_orders": 938,
    "unique_customers": 198,
    "total_net_revenue": 546438.09,
    "total_profit": 313330.39,
    "state_avg_order_value": 582.56
  },
  {
    "state": "CO",
    "total_orders": 781,
    "unique_customers": 183,
    "total_net_revenue": 498616.19,
    "total_profit": 280406.49,
    "state_avg_order_value": 638.43
  },
  {
    "state": "MA",
    "total_orders": 881,
    "unique_customers": 196,
    "total_net_revenue": 472679.47,
    "total_profit": 274378.17,
    "state_avg_order_value": 536.53
  }
]
```

### Query 13: Revenue by Top 20 Cities

- **Category**: Sales & Product Analytics
- **Rows Returned**: 20
- **Columns**: `['city', 'state', 'order_count', 'customer_count', 'total_net_revenue', 'total_profit']`

```json
[
  {
    "city": "Lakewood",
    "state": "CO",
    "order_count": 201,
    "customer_count": 40,
    "total_net_revenue": 143810.96,
    "total_profit": 79489.21
  },
  {
    "city": "Cleveland",
    "state": "OH",
    "order_count": 194,
    "customer_count": 35,
    "total_net_revenue": 140061.55,
    "total_profit": 78790.75
  },
  {
    "city": "Las Vegas",
    "state": "NV",
    "order_count": 201,
    "customer_count": 40,
    "total_net_revenue": 131779.05,
    "total_profit": 74747.45
  }
]
```

### Query 14: New vs Returning Customers by Month

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 34
- **Columns**: `['order_month', 'new_customer_orders', 'returning_customer_orders', 'new_customer_revenue', 'returning_customer_revenue', 'returning_revenue_share_pct']`

```json
[
  {
    "order_month": "2024-01",
    "new_customer_orders": 358,
    "returning_customer_orders": 0,
    "new_customer_revenue": 172987.7,
    "returning_customer_revenue": 0.0,
    "returning_revenue_share_pct": 0.0
  },
  {
    "order_month": "2024-02",
    "new_customer_orders": 369,
    "returning_customer_orders": 39,
    "new_customer_revenue": 232715.4,
    "returning_customer_revenue": 22099.24,
    "returning_revenue_share_pct": 8.67
  },
  {
    "order_month": "2024-03",
    "new_customer_orders": 364,
    "returning_customer_orders": 84,
    "new_customer_revenue": 177503.34,
    "returning_customer_revenue": 38289.09,
    "returning_revenue_share_pct": 17.74
  }
]
```

### Query 15: Repeat Purchase Rate (RPR)

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 1
- **Columns**: `['total_active_customers', 'single_order_customers', 'repeat_customers', 'repeat_purchase_rate_pct']`

```json
[
  {
    "total_active_customers": 5438,
    "single_order_customers": 676,
    "repeat_customers": 4762,
    "repeat_purchase_rate_pct": 87.57
  }
]
```

### Query 16: Average Customer Lifetime Value (CLV)

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 3
- **Columns**: `['customer_segment', 'total_customers', 'avg_orders_per_customer', 'avg_customer_lifetime_value_clv', 'avg_customer_lifetime_profit']`

```json
[
  {
    "customer_segment": "Small Business",
    "total_customers": 570,
    "avg_orders_per_customer": 4.39,
    "avg_customer_lifetime_value_clv": 2490.07,
    "avg_customer_lifetime_profit": 1441.97
  },
  {
    "customer_segment": "Corporate",
    "total_customers": 1131,
    "avg_orders_per_customer": 4.37,
    "avg_customer_lifetime_value_clv": 2462.81,
    "avg_customer_lifetime_profit": 1426.5
  },
  {
    "customer_segment": "Consumer",
    "total_customers": 3737,
    "avg_orders_per_customer": 4.34,
    "avg_customer_lifetime_value_clv": 2459.8,
    "avg_customer_lifetime_profit": 1418.92
  }
]
```

### Query 17: Top Spending Customers (VIPs)

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 20
- **Columns**: `['spend_rank', 'customer_id', 'customer_name', 'city', 'state', 'customer_segment', 'completed_orders', 'total_items_purchased', 'total_net_spend', 'total_profit_generated']`

```json
[
  {
    "spend_rank": 1,
    "customer_id": "CUST-11771",
    "customer_name": "Stephen Griffin",
    "city": "Springfield",
    "state": "IL",
    "customer_segment": "Consumer",
    "completed_orders": 10,
    "total_items_purchased": 36,
    "total_net_spend": 21140.55,
    "total_profit_generated": 11324.35
  },
  {
    "spend_rank": 2,
    "customer_id": "CUST-15336",
    "customer_name": "Keith Patterson",
    "city": "Syracuse",
    "state": "NY",
    "customer_segment": "Consumer",
    "completed_orders": 19,
    "total_items_purchased": 49,
    "total_net_spend": 19934.16,
    "total_profit_generated": 10944.61
  },
  {
    "spend_rank": 3,
    "customer_id": "CUST-11379",
    "customer_name": "Nicole Gomez",
    "city": "Winston-Salem",
    "state": "NC",
    "customer_segment": "Consumer",
    "completed_orders": 18,
    "total_items_purchased": 52,
    "total_net_spend": 19553.06,
    "total_profit_generated": 11145.36
  }
]
```

### Query 18: Products with Declining Sales using Window Functions

- **Category**: Sales & Product Analytics
- **Rows Returned**: 15
- **Columns**: `['product_id', 'product_name', 'category', 'sales_quarter', 'current_quarter_rev', 'prior_quarter_rev', 'revenue_decline_amount', 'decline_pct']`

```json
[
  {
    "product_id": "PROD-1026",
    "product_name": "Foldable Smartphone 256GB - Pro Edition",
    "category": "Electronics",
    "sales_quarter": "2026-Q3",
    "current_quarter_rev": 1790.72,
    "prior_quarter_rev": 47006.4,
    "revenue_decline_amount": -45215.68,
    "decline_pct": -96.19
  },
  {
    "product_id": "PROD-1032",
    "product_name": "Foldable Smartphone 256GB - Special Bundle",
    "category": "Electronics",
    "sales_quarter": "2026-Q1",
    "current_quarter_rev": 16256.38,
    "prior_quarter_rev": 38290.63,
    "revenue_decline_amount": -22034.25,
    "decline_pct": -57.54
  },
  {
    "product_id": "PROD-1043",
    "product_name": "Pro Gaming Laptop 16-inch - Plus",
    "category": "Electronics",
    "sales_quarter": "2026-Q1",
    "current_quarter_rev": 27358.9,
    "prior_quarter_rev": 48491.28,
    "revenue_decline_amount": -21132.38,
    "decline_pct": -43.58
  }
]
```

### Query 19: Discount vs Profit Analysis

- **Category**: Sales & Product Analytics
- **Rows Returned**: 4
- **Columns**: `['discount_tier', 'line_item_count', 'total_units_sold', 'total_gross_revenue', 'total_discount_amount', 'total_net_revenue', 'total_profit', 'effective_profit_margin_pct']`

```json
[
  {
    "discount_tier": "0% (Full Price)",
    "line_item_count": 18879,
    "total_units_sold": 28057,
    "total_gross_revenue": 6482190.26,
    "total_discount_amount": 0.0,
    "total_net_revenue": 6482190.26,
    "total_profit": 3939045.41,
    "effective_profit_margin_pct": 60.77
  },
  {
    "discount_tier": "1% - 10% (Low Discount)",
    "line_item_count": 12524,
    "total_units_sold": 18595,
    "total_gross_revenue": 4329469.34,
    "total_discount_amount": 329348.99,
    "total_net_revenue": 4000120.35,
    "total_profit": 2299752.95,
    "effective_profit_margin_pct": 57.49
  },
  {
    "discount_tier": "11% - 20% (Medium Discount)",
    "line_item_count": 8230,
    "total_units_sold": 12353,
    "total_gross_revenue": 2861990.22,
    "total_discount_amount": 486906.91,
    "total_net_revenue": 2375083.31,
    "total_profit": 1251848.81,
    "effective_profit_margin_pct": 52.71
  }
]
```

### Query 20: Revenue Contribution by Category and Cumulative Pareto %

- **Category**: Sales & Product Analytics
- **Rows Returned**: 5
- **Columns**: `['category', 'category_revenue', 'category_profit', 'pct_of_total_revenue', 'cumulative_pareto_revenue_pct']`

```json
[
  {
    "category": "Electronics",
    "category_revenue": 7838191.48,
    "category_profit": 4063443.78,
    "pct_of_total_revenue": 58.51,
    "cumulative_pareto_revenue_pct": 58.51
  },
  {
    "category": "Home & Kitchen",
    "category_revenue": 2594965.58,
    "category_profit": 1666649.53,
    "pct_of_total_revenue": 19.37,
    "cumulative_pareto_revenue_pct": 77.88
  },
  {
    "category": "Apparel & Fashion",
    "category_revenue": 1521533.78,
    "category_profit": 1058183.58,
    "pct_of_total_revenue": 11.36,
    "cumulative_pareto_revenue_pct": 89.23
  }
]
```

### Query 21: Monthly Active Customers (MAC / MAU)

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 34
- **Columns**: `['active_month', 'monthly_active_customers', 'total_monthly_orders', 'orders_per_active_customer', 'revenue_per_active_customer']`

```json
[
  {
    "active_month": "2024-01",
    "monthly_active_customers": 328,
    "total_monthly_orders": 358,
    "orders_per_active_customer": 1.09,
    "revenue_per_active_customer": 527.4
  },
  {
    "active_month": "2024-02",
    "monthly_active_customers": 382,
    "total_monthly_orders": 408,
    "orders_per_active_customer": 1.07,
    "revenue_per_active_customer": 667.05
  },
  {
    "active_month": "2024-03",
    "monthly_active_customers": 416,
    "total_monthly_orders": 448,
    "orders_per_active_customer": 1.08,
    "revenue_per_active_customer": 518.73
  }
]
```

### Query 22: Customer Cohort Retention Matrix

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 189
- **Columns**: `['cohort_month', 'total_cohort_size', 'month_number', 'active_users', 'retention_rate_pct']`

```json
[
  {
    "cohort_month": "2024-01",
    "total_cohort_size": 328,
    "month_number": 0,
    "active_users": 328,
    "retention_rate_pct": 100.0
  },
  {
    "cohort_month": "2024-01",
    "total_cohort_size": 328,
    "month_number": 1,
    "active_users": 35,
    "retention_rate_pct": 10.67
  },
  {
    "cohort_month": "2024-01",
    "total_cohort_size": 328,
    "month_number": 2,
    "active_users": 43,
    "retention_rate_pct": 13.11
  }
]
```

### Query 23: RFM Customer Segmentation (NTILE Scoring)

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 8
- **Columns**: `['rfm_segment', 'customer_count', 'avg_recency_days', 'avg_orders', 'avg_monetary_spend', 'total_segment_revenue', 'pct_revenue_contribution']`

```json
[
  {
    "rfm_segment": "Champions",
    "customer_count": 1011,
    "avg_recency_days": 24.2,
    "avg_orders": 8.63,
    "avg_monetary_spend": 5541.15,
    "total_segment_revenue": 5602104.2,
    "pct_revenue_contribution": 41.82
  },
  {
    "rfm_segment": "Loyal Customers",
    "customer_count": 1062,
    "avg_recency_days": 68.1,
    "avg_orders": 5.1,
    "avg_monetary_spend": 2952.36,
    "total_segment_revenue": 3135409.64,
    "pct_revenue_contribution": 23.4
  },
  {
    "rfm_segment": "At Risk Customers",
    "customer_count": 791,
    "avg_recency_days": 261.4,
    "avg_orders": 4.72,
    "avg_monetary_spend": 3238.22,
    "total_segment_revenue": 2561431.49,
    "pct_revenue_contribution": 19.12
  }
]
```

### Query 24: Top 10% Decile Customer Contribution to Revenue (NTILE(10))

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 10
- **Columns**: `['spend_decile', 'customer_count', 'min_spend_in_decile', 'max_spend_in_decile', 'total_decile_revenue', 'decile_revenue_share_pct']`

```json
[
  {
    "spend_decile": 10,
    "customer_count": 543,
    "min_spend_in_decile": 5811.61,
    "max_spend_in_decile": 21140.55,
    "total_decile_revenue": 4701366.06,
    "decile_revenue_share_pct": 35.09
  },
  {
    "spend_decile": 9,
    "customer_count": 543,
    "min_spend_in_decile": 3949.22,
    "max_spend_in_decile": 5797.79,
    "total_decile_revenue": 2609526.69,
    "decile_revenue_share_pct": 19.48
  },
  {
    "spend_decile": 8,
    "customer_count": 544,
    "min_spend_in_decile": 2853.85,
    "max_spend_in_decile": 3949.18,
    "total_decile_revenue": 1813041.86,
    "decile_revenue_share_pct": 13.53
  }
]
```

### Query 25: Churn Risk Detection (Inactive > 90 / 180 Days with Repeat Order History)

- **Category**: Customer Intelligence & Retention
- **Rows Returned**: 25
- **Columns**: `['customer_id', 'customer_name', 'email', 'city', 'state', 'historic_orders', 'historic_lifetime_spend', 'last_order_date', 'days_inactive', 'churn_risk_tier']`

```json
[
  {
    "customer_id": "CUST-11771",
    "customer_name": "Stephen Griffin",
    "email": "stephen.griffin654@corporate.com",
    "city": "Springfield",
    "state": "IL",
    "historic_orders": 10,
    "historic_lifetime_spend": 21140.55,
    "last_order_date": "2026-01-10",
    "days_inactive": 171,
    "churn_risk_tier": "Moderate Churn Risk (3-6 Months Inactive)"
  },
  {
    "customer_id": "CUST-11379",
    "customer_name": "Nicole Gomez",
    "email": "nicole.gomez68@icloud.com",
    "city": "Winston-Salem",
    "state": "NC",
    "historic_orders": 18,
    "historic_lifetime_spend": 19553.06,
    "last_order_date": "2026-03-23",
    "days_inactive": 99,
    "churn_risk_tier": "Moderate Churn Risk (3-6 Months Inactive)"
  },
  {
    "customer_id": "CUST-10505",
    "customer_name": "Brian Mason",
    "email": "brian.mason736@icloud.com",
    "city": "Charleston",
    "state": "SC",
    "historic_orders": 16,
    "historic_lifetime_spend": 18679.45,
    "last_order_date": "2025-10-02",
    "days_inactive": 271,
    "churn_risk_tier": "Severe Churn Risk (9+ Months Inactive)"
  }
]
```

