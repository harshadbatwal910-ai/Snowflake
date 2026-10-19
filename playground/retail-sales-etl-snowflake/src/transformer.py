"""
src/transformer.py
──────────────────
Lightweight transformations applied to the raw DataFrames before they
are written to Snowflake.  The goal is to normalise column types and
remove obviously bad records — heavy business logic lives in SQL.
"""

from __future__ import annotations

import pandas as pd


def _strip_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case and strip whitespace from all column names."""
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_column_names(df)
    # Drop rows with no order_id — they cannot be joined to anything
    df = df.dropna(subset=["order_id"])
    df["order_id"] = df["order_id"].str.strip()
    return df


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_column_names(df)
    df = df.dropna(subset=["order_id"])
    # Clamp negative prices to 0 so SQL aggregations are non-negative
    df["price"] = df["price"].clip(lower=0)
    df["freight_value"] = df["freight_value"].clip(lower=0)
    return df


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_column_names(df)
    df = df.dropna(subset=["customer_id"])
    df["customer_state"] = df["customer_state"].str.upper().str.strip()
    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_column_names(df)
    df = df.dropna(subset=["product_id"])
    df["product_category_name"] = (
        df["product_category_name"].fillna("unknown").str.strip()
    )
    return df


def transform_order_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_column_names(df)
    df = df.dropna(subset=["order_id"])
    df["payment_value"] = df["payment_value"].clip(lower=0)
    return df


# Dispatch table — keys match the extractor's dataset names
TRANSFORMERS = {
    "orders":         transform_orders,
    "order_items":    transform_order_items,
    "customers":      transform_customers,
    "products":       transform_products,
    "order_payments": transform_order_payments,
}


def transform_all(
    raw: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Apply the appropriate transformation to every extracted DataFrame.

    Args:
        raw: mapping from dataset name to raw DataFrame (from extractor).

    Returns:
        New mapping with transformed DataFrames.
    """
    print("\n[transformer] Applying transformations ...")
    result: dict[str, pd.DataFrame] = {}
    for name, df in raw.items():
        fn = TRANSFORMERS.get(name)
        if fn is None:
            raise KeyError(f"No transformer registered for dataset '{name}'")
        result[name] = fn(df)
        print(f"  [transform] {name}: {len(result[name]):,} rows after cleaning")
    return result
