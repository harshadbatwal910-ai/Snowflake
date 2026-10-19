-- =============================================================
-- 03_data_quality.sql
-- Data quality checks against the RAW schema.
-- Each SELECT returns rows that violate the rule.
-- A healthy dataset returns 0 rows for every check.
-- =============================================================

USE DATABASE RETAIL_SALES;
USE SCHEMA   RAW;

-- ── Check 1: Duplicate order IDs in ORDERS ────────────────
-- Expectation: each order_id appears exactly once.
SELECT
    'duplicate_order_ids' AS check_name,
    order_id,
    COUNT(*)              AS occurrences
FROM   ORDERS
GROUP BY order_id
HAVING COUNT(*) > 1;

-- ── Check 2: Orders with no matching items ────────────────
-- Every delivered/invoiced order should have at least one item.
SELECT
    'orders_without_items' AS check_name,
    o.order_id,
    o.order_status
FROM   ORDERS AS o
LEFT JOIN ORDER_ITEMS AS oi ON o.order_id = oi.order_id
WHERE  oi.order_id IS NULL
  AND  o.order_status NOT IN ('canceled', 'unavailable');

-- ── Check 3: Order items with invalid prices ──────────────
-- price and freight_value must be >= 0.
SELECT
    'invalid_price_or_freight' AS check_name,
    order_id,
    order_item_id,
    price,
    freight_value
FROM   ORDER_ITEMS
WHERE  price < 0
   OR  freight_value < 0;

-- ── Check 4: Missing customer IDs on orders ───────────────
SELECT
    'orders_missing_customer_id' AS check_name,
    order_id
FROM   ORDERS
WHERE  customer_id IS NULL;

-- ── Check 5: Orphan order items (no parent order) ─────────
SELECT
    'orphan_order_items' AS check_name,
    oi.order_id,
    oi.order_item_id
FROM   ORDER_ITEMS AS oi
LEFT JOIN ORDERS AS o ON oi.order_id = o.order_id
WHERE  o.order_id IS NULL;

-- ── Check 6: Products missing a category ─────────────────
SELECT
    'products_missing_category' AS check_name,
    COUNT(*) AS missing_count
FROM   PRODUCTS
WHERE  product_category_name IS NULL
    OR TRIM(product_category_name) = '';

-- ── Check 7: Payments with zero or negative value ────────
SELECT
    'invalid_payment_value' AS check_name,
    order_id,
    payment_sequential,
    payment_value
FROM   ORDER_PAYMENTS
WHERE  payment_value <= 0;
