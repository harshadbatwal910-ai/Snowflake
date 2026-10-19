"""
tests/test_transformer.py
─────────────────────────
Unit tests for src/transformer.py.
All tests use in-memory DataFrames — no Snowflake or file-system access required.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.transformer import (
    transform_customers,
    transform_order_items,
    transform_order_payments,
    transform_orders,
    transform_products,
    transform_all,
)


# ── transform_orders ──────────────────────────────────────

class TestTransformOrders:
    def test_drops_rows_with_null_order_id(self):
        df = pd.DataFrame({
            "order_id":     ["abc", None, "def"],
            "customer_id":  ["c1", "c2", "c3"],
            "order_status": ["delivered", "delivered", "delivered"],
        })
        result = transform_orders(df)
        assert len(result) == 2
        assert result["order_id"].notna().all()

    def test_strips_order_id_whitespace(self):
        df = pd.DataFrame({
            "order_id":     ["  abc  ", "def "],
            "customer_id":  ["c1", "c2"],
            "order_status": ["delivered", "shipped"],
        })
        result = transform_orders(df)
        assert list(result["order_id"]) == ["abc", "def"]

    def test_column_names_lowercased(self):
        df = pd.DataFrame({"ORDER_ID": ["x"], "CUSTOMER_ID": ["y"], "ORDER_STATUS": ["z"]})
        result = transform_orders(df)
        assert "order_id" in result.columns
        assert "ORDER_ID" not in result.columns


# ── transform_order_items ─────────────────────────────────

class TestTransformOrderItems:
    def test_clips_negative_price_to_zero(self):
        df = pd.DataFrame({
            "order_id":      ["o1"],
            "order_item_id": [1],
            "price":         [-5.0],
            "freight_value": [3.0],
        })
        result = transform_order_items(df)
        assert result["price"].iloc[0] == 0.0

    def test_clips_negative_freight_to_zero(self):
        df = pd.DataFrame({
            "order_id":      ["o1"],
            "order_item_id": [1],
            "price":         [10.0],
            "freight_value": [-2.5],
        })
        result = transform_order_items(df)
        assert result["freight_value"].iloc[0] == 0.0

    def test_positive_values_unchanged(self):
        df = pd.DataFrame({
            "order_id":      ["o1"],
            "order_item_id": [1],
            "price":         [99.99],
            "freight_value": [12.50],
        })
        result = transform_order_items(df)
        assert result["price"].iloc[0] == pytest.approx(99.99)
        assert result["freight_value"].iloc[0] == pytest.approx(12.50)

    def test_drops_rows_with_null_order_id(self):
        df = pd.DataFrame({
            "order_id":      [None, "o2"],
            "order_item_id": [1, 2],
            "price":         [10.0, 20.0],
            "freight_value": [1.0, 2.0],
        })
        result = transform_order_items(df)
        assert len(result) == 1


# ── transform_customers ───────────────────────────────────

class TestTransformCustomers:
    def test_state_is_uppercased(self):
        df = pd.DataFrame({
            "customer_id":    ["c1"],
            "customer_state": ["sp"],
        })
        result = transform_customers(df)
        assert result["customer_state"].iloc[0] == "SP"

    def test_state_whitespace_stripped(self):
        df = pd.DataFrame({
            "customer_id":    ["c1"],
            "customer_state": [" rj "],
        })
        result = transform_customers(df)
        assert result["customer_state"].iloc[0] == "RJ"

    def test_drops_null_customer_id(self):
        df = pd.DataFrame({
            "customer_id":    [None, "c2"],
            "customer_state": ["SP", "RJ"],
        })
        result = transform_customers(df)
        assert len(result) == 1


# ── transform_products ────────────────────────────────────

class TestTransformProducts:
    def test_null_category_filled_with_unknown(self):
        df = pd.DataFrame({
            "product_id":             ["p1"],
            "product_category_name":  [None],
        })
        result = transform_products(df)
        assert result["product_category_name"].iloc[0] == "unknown"

    def test_category_whitespace_stripped(self):
        df = pd.DataFrame({
            "product_id":             ["p1"],
            "product_category_name":  ["  electronics  "],
        })
        result = transform_products(df)
        assert result["product_category_name"].iloc[0] == "electronics"

    def test_drops_null_product_id(self):
        df = pd.DataFrame({
            "product_id":            [None, "p2"],
            "product_category_name": ["books", "toys"],
        })
        result = transform_products(df)
        assert len(result) == 1


# ── transform_order_payments ──────────────────────────────

class TestTransformOrderPayments:
    def test_clips_negative_payment_value(self):
        df = pd.DataFrame({
            "order_id":      ["o1"],
            "payment_value": [-50.0],
        })
        result = transform_order_payments(df)
        assert result["payment_value"].iloc[0] == 0.0

    def test_valid_payment_value_unchanged(self):
        df = pd.DataFrame({
            "order_id":      ["o1"],
            "payment_value": [250.75],
        })
        result = transform_order_payments(df)
        assert result["payment_value"].iloc[0] == pytest.approx(250.75)


# ── transform_all ─────────────────────────────────────────

class TestTransformAll:
    def _minimal_raw(self) -> dict:
        return {
            "orders": pd.DataFrame({
                "order_id": ["o1"], "customer_id": ["c1"], "order_status": ["delivered"],
            }),
            "order_items": pd.DataFrame({
                "order_id": ["o1"], "order_item_id": [1], "price": [10.0], "freight_value": [2.0],
            }),
            "customers": pd.DataFrame({
                "customer_id": ["c1"], "customer_state": ["sp"],
            }),
            "products": pd.DataFrame({
                "product_id": ["p1"], "product_category_name": ["books"],
            }),
            "order_payments": pd.DataFrame({
                "order_id": ["o1"], "payment_value": [12.0],
            }),
        }

    def test_returns_all_keys(self):
        result = transform_all(self._minimal_raw())
        assert set(result.keys()) == {
            "orders", "order_items", "customers", "products", "order_payments"
        }

    def test_raises_for_unknown_dataset(self):
        raw = self._minimal_raw()
        raw["unknown_table"] = pd.DataFrame({"a": [1]})
        with pytest.raises(KeyError, match="unknown_table"):
            transform_all(raw)
