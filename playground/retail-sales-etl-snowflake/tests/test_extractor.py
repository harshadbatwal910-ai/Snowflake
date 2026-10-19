"""
tests/test_extractor.py
───────────────────────
Unit tests for src/extractor.py.
Uses temporary CSV files so no real Olist data is required.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.extractor import extract_all, _CSV_MAP


@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> Path:
    """Create a temporary data/raw directory populated with minimal CSV stubs."""
    # Minimal valid CSVs — just enough columns to satisfy the extractor
    files = {
        "olist_orders_dataset.csv": (
            "order_id,customer_id,order_status,"
            "order_purchase_timestamp,order_approved_at,"
            "order_delivered_carrier_date,order_delivered_customer_date,"
            "order_estimated_delivery_date\n"
            "o1,c1,delivered,2018-01-01 10:00:00,2018-01-01 11:00:00,,,\n"
        ),
        "olist_order_items_dataset.csv": (
            "order_id,order_item_id,product_id,seller_id,"
            "shipping_limit_date,price,freight_value\n"
            "o1,1,p1,s1,2018-01-05 00:00:00,100.0,10.0\n"
        ),
        "olist_customers_dataset.csv": (
            "customer_id,customer_unique_id,customer_zip_code_prefix,"
            "customer_city,customer_state\n"
            "c1,u1,01001,Sao Paulo,SP\n"
        ),
        "olist_products_dataset.csv": (
            "product_id,product_category_name,product_name_lenght,"
            "product_description_lenght,product_photos_qty,"
            "product_weight_g,product_length_cm,product_height_cm,product_width_cm\n"
            "p1,electronics,10,50,3,500,20,10,15\n"
        ),
        "olist_order_payments_dataset.csv": (
            "order_id,payment_sequential,payment_type,payment_installments,payment_value\n"
            "o1,1,credit_card,1,110.0\n"
        ),
    }
    for filename, content in files.items():
        (tmp_path / filename).write_text(content)
    return tmp_path


class TestExtractAll:
    def test_returns_all_five_datasets(self, tmp_data_dir: Path):
        result = extract_all(data_dir=tmp_data_dir)
        assert set(result.keys()) == set(_CSV_MAP.keys())

    def test_orders_has_expected_columns(self, tmp_data_dir: Path):
        result = extract_all(data_dir=tmp_data_dir)
        assert "order_id" in result["orders"].columns
        assert "order_status" in result["orders"].columns

    def test_order_items_row_count(self, tmp_data_dir: Path):
        result = extract_all(data_dir=tmp_data_dir)
        assert len(result["order_items"]) == 1

    def test_missing_csv_raises_file_not_found(self, tmp_path: Path):
        # Empty directory — no CSVs present
        with pytest.raises(FileNotFoundError, match="olist_orders_dataset.csv"):
            extract_all(data_dir=tmp_path)
