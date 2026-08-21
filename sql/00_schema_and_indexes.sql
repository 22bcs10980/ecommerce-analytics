-- ============================================================================
-- E-COMMERCE ANALYTICS PLATFORM - SCHEMA & INDEXES DEFINITIONS
-- Database: SQLite (data/processed/cleaned_ecommerce.db)
-- ============================================================================

-- 1. CUSTOMERS TABLE
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(30) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50),
    address VARCHAR(200),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(10) NOT NULL,
    zip_code VARCHAR(20),
    country VARCHAR(50) DEFAULT 'United States',
    signup_date DATE NOT NULL,
    customer_segment VARCHAR(50) NOT NULL
);

-- 2. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(30) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    retail_price DECIMAL(10,2) NOT NULL,
    weight_kg DECIMAL(6,2)
);

-- 3. ORDERS TABLE
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(40) PRIMARY KEY,
    customer_id VARCHAR(30) NOT NULL,
    order_date DATE NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    shipping_city VARCHAR(100) NOT NULL,
    shipping_state VARCHAR(10) NOT NULL,
    shipping_cost DECIMAL(10,2) DEFAULT 0.00,
    delivery_days INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 4. ORDER ITEMS TABLE (With Calculated Business Metrics)
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id VARCHAR(40) PRIMARY KEY,
    order_id VARCHAR(40) NOT NULL,
    product_id VARCHAR(30) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    discount_rate DECIMAL(4,2) DEFAULT 0.00,
    gross_revenue DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) NOT NULL,
    net_revenue DECIMAL(12,2) NOT NULL,
    total_cost DECIMAL(12,2) NOT NULL,
    profit DECIMAL(12,2) NOT NULL,
    profit_margin_pct DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 5. PAYMENTS TABLE
CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(40) PRIMARY KEY,
    order_id VARCHAR(40) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- ============================================================================
-- HIGH-PERFORMANCE ANALYTICAL INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_order_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_sub_category ON products(sub_category);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_customers_state ON customers(state);
CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(customer_segment);