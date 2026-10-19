# Setup Guide

Step-by-step instructions to run the Retail Sales ETL pipeline and dashboard.
Commands are for PowerShell on Windows; macOS / Linux equivalents are noted where they differ.

## Prerequisites

- **Python 3.12** (recommended). The pinned `pandas==2.2.2` has no prebuilt wheel for Python 3.14, so installation fails there.
- A **Snowflake account** (the [free trial](https://signup.snowflake.com) is enough).
- A free **Kaggle** account to download the dataset.

Check which Python versions are installed:

```powershell
py -0p
```

If 3.12 is missing:

```powershell
winget install -e --id Python.Python.3.12 --scope user
```

---

## Step 1 — Create the virtual environment

Run from the project root.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

## Step 2 — Verify the install

```powershell
python -m pytest -v
```

Expect all tests to pass. They use in-memory data and need no Snowflake connection.

## Step 3 — Download the dataset

1. Download the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle and unzip it.
2. Copy these five files into `data\raw\`:

   - `olist_orders_dataset.csv`
   - `olist_order_items_dataset.csv`
   - `olist_customers_dataset.csv`
   - `olist_products_dataset.csv`
   - `olist_order_payments_dataset.csv`

3. Confirm they are in place:

```powershell
Get-ChildItem data\raw
```

## Step 4 — Find your Snowflake account identifier

In Snowsight: click your name (bottom-left) → **Account** → **View account details** → copy the **Account identifier**.

It looks like `ORGNAME-ACCOUNTNAME` (for example `myorg-xy12345`).
Use the identifier only: no `https://` and no `.snowflakecomputing.com`.

## Step 5 — Create the Snowflake objects

1. In Snowsight, open a new SQL worksheet.
2. Paste the contents of [`sql/01_create_database.sql`](sql/01_create_database.sql).
3. Select **Run All**, using the `SYSADMIN` role.

This creates the `RETAIL_WH` warehouse, the `RETAIL_SALES` database, the `RAW` and `ANALYTICS` schemas, and the five RAW tables.

## Step 6 — Configure credentials

```powershell
Copy-Item .env.example .env
notepad .env
```

Replace the three placeholders and leave the rest unchanged:

```
SNOWFLAKE_ACCOUNT=myorg-xy12345
SNOWFLAKE_USER=YOUR_LOGIN_USERNAME
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=RETAIL_SALES
SNOWFLAKE_WAREHOUSE=RETAIL_WH
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_ROLE=SYSADMIN
```

`.env` is git-ignored. Never commit it.

## Step 7 — Run the ETL pipeline

```powershell
python -m src.main
```

The pipeline extracts the five CSVs, cleans them, and loads them into Snowflake `RAW`.
Each run truncates the tables first, so it is safe to re-run.

Expected output ends with:

```
[load] ORDERS: 99,441 rows loaded (1 chunk(s))
...
[main] Pipeline completed in ~25s
```

## Step 8 — Create the analytics views

In a Snowsight worksheet, run [`sql/02_analytics_views.sql`](sql/02_analytics_views.sql).

## Step 9 — Run data quality checks (optional)

In a Snowsight worksheet, run [`sql/03_data_quality.sql`](sql/03_data_quality.sql).
Each query returns only rows that violate a rule; a clean dataset returns zero rows.

## Step 10 — Launch the dashboard

```powershell
streamlit run dashboard/app.py
```

Open <http://localhost:8501>. Query results are cached for 5 minutes. Press **C** in the browser and choose **Clear cache** to force a refresh.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `pip install` fails building `pandas` (`vswhere.exe` / meson error) | You are on Python 3.14. Recreate the venv with `py -3.12 -m venv .venv`. |
| `.venv\Scripts\Activate.ps1` is blocked | Run `Set-ExecutionPolicy -Scope Process RemoteSigned`. |
| `FileNotFoundError` for a CSV | Check that all five files are in `data\raw\` with the exact names in Step 3. |
| `404 Not Found ... your_account_identifier.snowflakecomputing.com` | `.env` still has placeholder values. Set the real account, user and password (Steps 4 and 6). |
| `390100 Incorrect username or password` | The account is correct but the credentials are not. Check `SNOWFLAKE_USER` and `SNOWFLAKE_PASSWORD`. |
| `Object does not exist` / `Insufficient privileges` | Step 5 was not run, or your user cannot use the `SYSADMIN` role. Change `SNOWFLAKE_ROLE` if needed. |
| `Missing optional dependency: pandas` | Reinstall dependencies: `pip install -r requirements.txt`. The file includes `snowflake-connector-python[pandas]` and `pyarrow`. |
| `pyarrow requires NumPy 2.0 or newer` | `pyarrow` is not the pinned version. Run `pip install pyarrow==16.1.0`. |
| Dashboard error `252005: Failed to convert ...` or dates in year 58033 | Timestamps were loaded with the wrong unit. Re-run Step 7 (the loader uses `use_logical_type=True`), then clear the Streamlit cache. |
| Dashboard shows no data or a missing view error | Steps 7 and 8 must both be completed. |
