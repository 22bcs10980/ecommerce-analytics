# Data Cleaning, Validation & Quality Audit Report

**Execution Timestamp:** 2026-08-19 18:42:08

**Target Database:** `data/processed/cleaned_ecommerce.db`

## 1. Dataset Row Count Reconciliation

| Table Name | Raw Rows | Cleaned Rows | Rows Dropped/Resolved | Duplicate Records Fixed |
| :--- | :---: | :---: | :---: | :---: |
| **customers** | 5,527 | 5,500 | 27 | 27 |
| **products** | 553 | 553 | 0 | 0 |
| **orders** | 26,078 | 26,000 | 78 | 78 |
| **order_items** | 45,887 | 45,887 | 0 | 0 |
| **payments** | 26,000 | 26,000 | 0 | 0 |

## 2. Key Data Cleaning & Imputation Decisions

| Table | Issue Identified | Cleaning / Imputation Strategy | Business Rationale | Impact Count |
| :--- | :--- | :--- | :--- | :---: |
| `customers` | Duplicate customer records | Deduplicate on customer_id keeping first | Guarantees primary key uniqueness | 27 |
| `customers` | Missing phone numbers | Impute with Not Provided | Preserves customer records while flagging non-contactable channel | 142 |
| `customers` | Missing postal zip codes | Impute with 00000 | Preserves state/city geo-data without failing joins | 86 |
| `products` | Missing sub-category | Synthesize as General <Category> | Prevents null buckets in category drill-downs | 2 |
| `products` | Negative/zero prices | Take absolute value or apply 40% markup | Fixes entry transcription errors while preserving MSRP economics | 1 |
| `orders` | Duplicate orders | Deduplicate on order_id | Prevents double counting revenue | 78 |
| `order_items` | Missing discount rates | Impute with 0.0 (full price) | Missing promo defaults to standard MSRP | 378 |
| `order_items` | Financial metrics recomputation | Recomputed Gross/Net Revenue, Discount, Total Cost, Profit, Profit Margin % | Ensures 100% mathematical reconciliation across reports | 45,887 |

## 3. Referential Integrity & Validation Checks

- **Customers -> Orders**: 100% of orders reference valid primary key customer IDs.
- **Orders -> Order Items**: 100% of order items map to existing orders.
- **Products -> Order Items**: 100% of order items map to master catalog products.
- **Orders -> Payments**: 100% of payments map to valid order records.
- **Financial Calculation Check**: Gross Revenue = Net Revenue + Discount Amount; Net Revenue - Total Cost = Profit (0.00 variance).
