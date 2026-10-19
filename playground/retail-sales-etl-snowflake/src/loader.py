"""
src/loader.py
─────────────
Writes transformed DataFrames into Snowflake RAW tables using the
Snowflake Python connector and pandas write_pandas helper.
Each load truncates the target table first so the pipeline is
idempotent on full-refresh runs.
"""

from __future__ import annotations

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

from .config import SnowflakeConfig

# Map dataset name → Snowflake RAW table name (upper-case)
_TABLE_MAP: dict[str, str] = {
    "orders":         "ORDERS",
    "order_items":    "ORDER_ITEMS",
    "customers":      "CUSTOMERS",
    "products":       "PRODUCTS",
    "order_payments": "ORDER_PAYMENTS",
}


def _get_connection(cfg: SnowflakeConfig) -> snowflake.connector.SnowflakeConnection:
    return snowflake.connector.connect(
        account=cfg.account,
        user=cfg.user,
        password=cfg.password,
        database=cfg.database,
        warehouse=cfg.warehouse,
        schema=cfg.schema,
        role=cfg.role,
    )


def load_dataframe(
    conn: snowflake.connector.SnowflakeConnection,
    df,
    table_name: str,
    database: str,
    schema: str = "RAW",
) -> None:
    """Truncate *table_name* and bulk-load *df* into it.

    Args:
        conn:       open Snowflake connection.
        df:         pandas DataFrame whose columns match the target table.
        table_name: Snowflake table name (upper-case).
        database:   Snowflake database name.
        schema:     Snowflake schema name (default ``RAW``).
    """
    # Ensure column names are upper-case to match Snowflake DDL
    import pandas as pd  # local import to keep top-level deps minimal

    df = df.copy()
    df.columns = [c.upper() for c in df.columns]

    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE IF EXISTS {database}.{schema}.{table_name}")

    success, n_chunks, n_rows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        database=database,
        schema=schema,
        auto_create_table=False,
        overwrite=False,
        quote_identifiers=False,
        # Without this, datetime64 values are read with the wrong unit and
        # land in TIMESTAMP_NTZ columns as year ~500,000,000.
        use_logical_type=True,
    )

    if not success:
        raise RuntimeError(f"write_pandas failed for table {table_name}")

    print(f"  [load] {table_name}: {n_rows:,} rows loaded ({n_chunks} chunk(s))")


def load_all(
    transformed: dict,
    cfg: SnowflakeConfig,
) -> None:
    """Open one Snowflake connection and load every transformed DataFrame.

    Args:
        transformed: mapping from dataset name to cleaned DataFrame.
        cfg:         Snowflake connection config.
    """
    print(f"\n[loader] Connecting to Snowflake account: {cfg.account} ...")
    conn = _get_connection(cfg)

    try:
        for name, df in transformed.items():
            table = _TABLE_MAP[name]
            load_dataframe(conn, df, table, cfg.database, cfg.schema)
    finally:
        conn.close()
        print("[loader] Connection closed.")
