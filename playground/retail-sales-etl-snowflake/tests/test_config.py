"""
tests/test_config.py
────────────────────
Unit tests for src/config.py.
"""

from __future__ import annotations

import os

import pytest

from src.config import get_snowflake_config, SnowflakeConfig

_VALID_ENV = {
    "SNOWFLAKE_ACCOUNT":   "my_account",
    "SNOWFLAKE_USER":      "my_user",
    "SNOWFLAKE_PASSWORD":  "secret",
    "SNOWFLAKE_DATABASE":  "RETAIL_SALES",
    "SNOWFLAKE_WAREHOUSE": "RETAIL_WH",
    "SNOWFLAKE_SCHEMA":    "RAW",
    "SNOWFLAKE_ROLE":      "SYSADMIN",
}


class TestGetSnowflakeConfig:
    def test_returns_snowflake_config(self, monkeypatch):
        for k, v in _VALID_ENV.items():
            monkeypatch.setenv(k, v)
        cfg = get_snowflake_config()
        assert isinstance(cfg, SnowflakeConfig)

    def test_values_mapped_correctly(self, monkeypatch):
        for k, v in _VALID_ENV.items():
            monkeypatch.setenv(k, v)
        cfg = get_snowflake_config()
        assert cfg.account   == "my_account"
        assert cfg.user      == "my_user"
        assert cfg.password  == "secret"
        assert cfg.database  == "RETAIL_SALES"
        assert cfg.warehouse == "RETAIL_WH"
        assert cfg.schema    == "RAW"
        assert cfg.role      == "SYSADMIN"

    def test_raises_on_missing_variable(self, monkeypatch):
        for k, v in _VALID_ENV.items():
            monkeypatch.setenv(k, v)
        monkeypatch.delenv("SNOWFLAKE_PASSWORD")
        with pytest.raises(EnvironmentError, match="SNOWFLAKE_PASSWORD"):
            get_snowflake_config()

    def test_config_is_immutable(self, monkeypatch):
        for k, v in _VALID_ENV.items():
            monkeypatch.setenv(k, v)
        cfg = get_snowflake_config()
        with pytest.raises((AttributeError, TypeError)):
            cfg.account = "hacked"  # type: ignore[misc]
