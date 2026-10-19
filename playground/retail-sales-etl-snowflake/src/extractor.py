"""
src/extractor.py
────────────────
Reads the Olist CSV files from data/raw/ into pandas DataFrames.
Each public function returns a clean DataFrame ready for loading.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Canonical CSV file names as shipped by Kaggle
_CSV_MAP: dict[str, str] = {
    "orders":         "olist_orders_dataset.csv",
    "order_items":    "olist_order_items_dataset.csv",
    "customers":      "olist_customers_dataset.csv",
    "products":       "olist_products_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
}

# Timestamp columns that need explicit parsing
_TIMESTAMP_COLS: dict[str, list[str]] = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
}


def _read_csv(name: str, data_dir: Path) -> pd.DataFrame:
    path = data_dir / _CSV_MAP[name]
    if not path.exists():
        raise FileNotFoundError(
            f"Expected CSV not found: {path}\n"
            "Download the Olist dataset from Kaggle and place the files in data/raw/."
        )
    parse_dates = _TIMESTAMP_COLS.get(name)
    df = pd.read_csv(path, parse_dates=parse_dates, low_memory=False)
    print(f"  [extract] {name}: {len(df):,} rows, {len(df.columns)} columns")
    return df


def extract_all(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    """Extract all five Olist CSV files and return them as a dict of DataFrames.

    Args:
        data_dir: path to the directory containing the CSV files.
                  Defaults to ``<project_root>/data/raw``.

    Returns:
        Mapping from dataset name to DataFrame.
    """
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[1] / "data" / "raw"

    print(f"\n[extractor] Reading CSVs from: {data_dir}")
    return {name: _read_csv(name, data_dir) for name in _CSV_MAP}
