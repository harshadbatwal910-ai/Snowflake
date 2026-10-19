-- =============================================================
-- 02_analytics_views.sql
-- Creates analytics views in the ANALYTICS schema on top of RAW
-- tables.  Execute after the ETL pipeline has populated RAW.
-- =============================================================

USE DATABASE RETAIL_SALES;
USE SCHEMA   ANALYTICS;

-- ── 1. Daily sales trend ──────────────────────────────────
-- Revenue = sum of (price + freight_value) per calendar day.
CREATE OR REPLACE VIEW VW_DAILY_SALES AS
SELECT
    DATE_TRUNC('DAY', o.order_purchase_timestamp)   AS sale_date,
    COUNT(DISTINCT o.order_id)                       AS order_count,
    SUM(oi.price)                                    AS total_price,
    SUM(oi.freight_value)                            AS total_freight,
    SUM(oi.price + oi.freight_value)                 AS total_revenue
FROM   RAW.ORDERS      AS o
JOIN   RAW.ORDER_ITEMS AS oi ON o.order_id = oi.order_id
WHERE  o.order_purchase_timestamp IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- ── 2. Revenue by product category ───────────────────────
CREATE OR REPLACE VIEW VW_CATEGORY_REVENUE AS
SELECT
    COALESCE(p.product_category_name, 'unknown')     AS category,
    COUNT(DISTINCT oi.order_id)                       AS order_count,
    SUM(oi.price)                                     AS total_price,
    SUM(oi.freight_value)                             AS total_freight,
    SUM(oi.price + oi.freight_value)                  AS total_revenue,
    ROUND(AVG(oi.price), 2)                           AS avg_item_price
FROM   RAW.ORDER_ITEMS AS oi
LEFT JOIN RAW.PRODUCTS AS p  ON oi.product_id = p.product_id
GROUP BY 1
ORDER BY total_revenue DESC;

-- ── 3. Order status distribution ──────────────────────────
CREATE OR REPLACE VIEW VW_ORDER_STATUS AS
SELECT
    order_status,
    COUNT(*) AS order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_share
FROM   RAW.ORDERS
GROUP BY 1
ORDER BY order_count DESC;

-- ── 4. Payment method breakdown ───────────────────────────
CREATE OR REPLACE VIEW VW_PAYMENT_SUMMARY AS
SELECT
    payment_type,
    COUNT(DISTINCT order_id)        AS order_count,
    SUM(payment_value)              AS total_payment_value,
    ROUND(AVG(payment_value), 2)    AS avg_payment_value
FROM   RAW.ORDER_PAYMENTS
GROUP BY 1
ORDER BY total_payment_value DESC;

-- ── 5. Customer state summary ─────────────────────────────
CREATE OR REPLACE VIEW VW_CUSTOMER_STATE AS
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id)          AS order_count,
    SUM(oi.price + oi.freight_value)    AS total_revenue
FROM   RAW.CUSTOMERS   AS c
JOIN   RAW.ORDERS      AS o  ON c.customer_id  = o.customer_id
JOIN   RAW.ORDER_ITEMS AS oi ON o.order_id     = oi.order_id
GROUP BY 1
ORDER BY order_count DESC;
