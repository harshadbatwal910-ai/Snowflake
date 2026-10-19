-- =============================================================
-- 01_create_database.sql
-- Provisions the Snowflake database, warehouse, and schemas.
-- Run this once as SYSADMIN (or a role with sufficient privileges)
-- before executing the ETL pipeline.
-- =============================================================

-- ── Warehouse ──────────────────────────────────────────────
CREATE WAREHOUSE IF NOT EXISTS RETAIL_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND   = 60
    AUTO_RESUME    = TRUE
    COMMENT        = 'Warehouse for the retail sales ETL pipeline';

-- ── Database ───────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS RETAIL_SALES
    COMMENT = 'Olist Brazilian e-commerce data warehouse';

USE DATABASE RETAIL_SALES;

-- ── Schemas ────────────────────────────────────────────────
-- RAW: landing zone for CSV ingestion (one table per source file)
CREATE SCHEMA IF NOT EXISTS RAW
    COMMENT = 'Raw ingestion layer — data loaded as-is from CSV files';

-- ANALYTICS: SQL views and aggregation tables built on top of RAW
CREATE SCHEMA IF NOT EXISTS ANALYTICS
    COMMENT = 'Analytics layer — views and aggregated tables for reporting';

-- ── RAW tables ─────────────────────────────────────────────
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS ORDERS (
    order_id                          VARCHAR(50)   NOT NULL,
    customer_id                       VARCHAR(50),
    order_status                      VARCHAR(30),
    order_purchase_timestamp          TIMESTAMP_NTZ,
    order_approved_at                 TIMESTAMP_NTZ,
    order_delivered_carrier_date      TIMESTAMP_NTZ,
    order_delivered_customer_date     TIMESTAMP_NTZ,
    order_estimated_delivery_date     TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    order_id              VARCHAR(50)   NOT NULL,
    order_item_id         INTEGER,
    product_id            VARCHAR(50),
    seller_id             VARCHAR(50),
    shipping_limit_date   TIMESTAMP_NTZ,
    price                 NUMBER(12, 2),
    freight_value         NUMBER(12, 2)
);

CREATE TABLE IF NOT EXISTS CUSTOMERS (
    customer_id              VARCHAR(50)  NOT NULL,
    customer_unique_id       VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city            VARCHAR(100),
    customer_state           VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS PRODUCTS (
    product_id                     VARCHAR(50)  NOT NULL,
    product_category_name          VARCHAR(100),
    product_name_lenght            INTEGER,
    product_description_lenght     INTEGER,
    product_photos_qty             INTEGER,
    product_weight_g               NUMBER(10, 2),
    product_length_cm              NUMBER(10, 2),
    product_height_cm              NUMBER(10, 2),
    product_width_cm               NUMBER(10, 2)
);

CREATE TABLE IF NOT EXISTS ORDER_PAYMENTS (
    order_id                VARCHAR(50)   NOT NULL,
    payment_sequential      INTEGER,
    payment_type            VARCHAR(30),
    payment_installments    INTEGER,
    payment_value           NUMBER(12, 2)
);
