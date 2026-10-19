"""
src/main.py
───────────
Entry point for the ETL pipeline.

Usage:
    python -m src.main

Steps:
    1. Extract  – read Olist CSV files from data/raw/
    2. Transform – clean and normalise DataFrames
    3. Load     – bulk-load into Snowflake RAW schema
"""

from __future__ import annotations

import sys
import time

from .config import get_snowflake_config
from .extractor import extract_all
from .loader import load_all
from .transformer import transform_all


def run() -> None:
    start = time.perf_counter()
    print("=" * 60)
    print("  Retail Sales ETL Pipeline — Olist Brazilian E-Commerce")
    print("=" * 60)

    # ── 1. Extract ────────────────────────────────────────
    raw = extract_all()

    # ── 2. Transform ──────────────────────────────────────
    transformed = transform_all(raw)

    # ── 3. Load ───────────────────────────────────────────
    cfg = get_snowflake_config()
    load_all(transformed, cfg)

    elapsed = time.perf_counter() - start
    print(f"\n[main] Pipeline completed in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run()
    except (FileNotFoundError, EnvironmentError) as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
