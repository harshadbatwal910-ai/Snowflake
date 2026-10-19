# Retail Sales ETL Pipeline with Snowflake

An end-to-end data engineering project that processes the
[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
dataset using Python, Snowflake SQL, and Streamlit.

---

## Architecture

```
Olist CSV Files
      │
      ▼
Python ETL (src/)
  extract → transform → load
      │
      ▼
Snowflake RAW schema
  ORDERS · ORDER_ITEMS · CUSTOMERS · PRODUCTS · ORDER_PAYMENTS
      │
      ▼
Snowflake ANALYTICS schema (sql/02_analytics_views.sql)
  VW_DAILY_SALES · VW_CATEGORY_REVENUE · VW_ORDER_STATUS
  VW_PAYMENT_SUMMARY · VW_CUSTOMER_STATE
      │
      ▼
Streamlit Dashboard (dashboard/app.py)
```

---

## Tech Stack

| Layer         | Technology                        |
|---------------|-----------------------------------|
| Extraction    | Python · Pandas                   |
| Storage       | Snowflake (cloud data warehouse)  |
| Transformation| Snowflake SQL                     |
| Orchestration | Python (`src/main.py`)            |
| Dashboard     | Streamlit · Plotly                |
| Testing       | Pytest                            |
| Version control | Git / GitHub                   |

---

## Dataset

Source: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

Five CSV files are used:

| File | Description |
|------|-------------|
| `olist_orders_dataset.csv` | Order header records |
| `olist_order_items_dataset.csv` | Line items per order |
| `olist_customers_dataset.csv` | Customer master data |
| `olist_products_dataset.csv` | Product catalogue |
| `olist_order_payments_dataset.csv` | Payment records |

> **Currency:** all financial values are in Brazilian reais (BRL).

---

## Project Structure

```
retail-sales-etl-snowflake/
├── data/
│   └── raw/                        # Place Olist CSV files here (git-ignored)
├── sql/
│   ├── 01_create_database.sql      # Provisions DB, warehouse, schemas, RAW tables
│   ├── 02_analytics_views.sql      # ANALYTICS layer views
│   └── 03_data_quality.sql         # DQ checks (each query returns violation rows)
├── src/
│   ├── __init__.py
│   ├── config.py                   # Snowflake credentials from environment
│   ├── extractor.py                # CSV → pandas DataFrames
│   ├── transformer.py              # Cleaning and normalisation
│   ├── loader.py                   # Bulk-load DataFrames into Snowflake RAW
│   └── main.py                     # Pipeline entry point
├── dashboard/
│   └── app.py                      # Streamlit dashboard
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_extractor.py
│   └── test_transformer.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

> A detailed walkthrough with troubleshooting is in [`SETUP.md`](SETUP.md).

### 1 — Download the dataset

Download the Olist dataset from Kaggle and unzip the CSV files into `data/raw/`.

### 2 — Python environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3 — Snowflake setup

Execute [`sql/01_create_database.sql`](sql/01_create_database.sql) in your Snowflake
worksheet (as `SYSADMIN` or an equivalent role).  This creates:

- Warehouse `RETAIL_WH`
- Database `RETAIL_SALES`
- Schemas `RAW` and `ANALYTICS`
- All five RAW tables

### 4 — Environment variables

Copy `.env.example` to `.env` and fill in your Snowflake credentials:

```
SNOWFLAKE_ACCOUNT=<your-account-identifier>
SNOWFLAKE_USER=<your-username>
SNOWFLAKE_PASSWORD=<your-password>
SNOWFLAKE_DATABASE=RETAIL_SALES
SNOWFLAKE_WAREHOUSE=RETAIL_WH
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_ROLE=SYSADMIN
```

> **Note:** `.env` is git-ignored and must never be committed.

### 5 — Run the ETL pipeline

```bash
python -m src.main
```

The pipeline extracts all five CSVs, applies lightweight transformations, and
bulk-loads every table into Snowflake RAW.

### 6 — Create analytics views

Execute [`sql/02_analytics_views.sql`](sql/02_analytics_views.sql) in your Snowflake
worksheet.

### 7 — Launch the dashboard

```bash
streamlit run dashboard/app.py
```

### 8 — Run the tests

```bash
python -m pytest -v
```

All tests are self-contained (in-memory DataFrames and temporary files) — no
Snowflake connection is required.

---

## Dashboard

| Widget | Description |
|--------|-------------|
| Total Orders | Count of all orders |
| Item Revenue | Sum of item prices (BRL) |
| Freight | Sum of freight values (BRL) |
| Payment Value | Total payment amounts (BRL) |
| Daily Sales Trend | Line chart of revenue over time |
| Top 10 Categories | Horizontal bar chart by revenue |
| Order Status | Donut chart of status distribution |
| Payment Methods | Bar chart by payment type |

---

## Data Quality

Run [`sql/03_data_quality.sql`](sql/03_data_quality.sql) to surface data issues.
Each query returns only rows that **violate** the rule — a clean dataset returns
zero rows for all checks.

| Check | Rule |
|-------|------|
| `duplicate_order_ids` | Each `order_id` appears exactly once in ORDERS |
| `orders_without_items` | Non-cancelled orders must have at least one item |
| `invalid_price_or_freight` | `price` and `freight_value` must be ≥ 0 |
| `orders_missing_customer_id` | All orders must have a `customer_id` |
| `orphan_order_items` | Every item must reference an existing order |
| `products_missing_category` | All products must have a category |
| `invalid_payment_value` | Payment values must be > 0 |

---

## Future Improvements

- Incremental data loading with idempotent processing
- ETL audit logs and structured error handling
- Snowflake Tasks and Streams for automated scheduling
- Star schema — fact and dimension tables
- Slowly Changing Dimensions (SCD Type 2)
- Apache Airflow orchestration
- CI/CD with GitHub Actions
- Dashboard deployment (Streamlit Community Cloud)

---

## Learning Outcomes

This project demonstrates practical experience with:

- Python-based ETL development
- Cloud data warehousing with Snowflake
- SQL transformations, joins, and analytical views
- Data quality validation patterns
- Interactive data visualisation with Streamlit and Plotly
- Unit testing ETL logic without external dependencies
