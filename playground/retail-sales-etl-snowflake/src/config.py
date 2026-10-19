"""
src/config.py
─────────────
Loads Snowflake connection settings from environment variables (or a
local .env file) and exposes them as a typed dataclass.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class SnowflakeConfig:
    account: str
    user: str
    password: str
    database: str
    warehouse: str
    schema: str
    role: str


def get_snowflake_config() -> SnowflakeConfig:
    """Read Snowflake credentials from environment variables.

    Raises:
        EnvironmentError: if any required variable is missing.
    """
    required = {
        "SNOWFLAKE_ACCOUNT":   "account",
        "SNOWFLAKE_USER":      "user",
        "SNOWFLAKE_PASSWORD":  "password",
        "SNOWFLAKE_DATABASE":  "database",
        "SNOWFLAKE_WAREHOUSE": "warehouse",
        "SNOWFLAKE_SCHEMA":    "schema",
        "SNOWFLAKE_ROLE":      "role",
    }

    values: dict[str, str] = {}
    missing: list[str] = []

    for env_var, field in required.items():
        value = os.getenv(env_var)
        if not value:
            missing.append(env_var)
        else:
            values[field] = value

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return SnowflakeConfig(**values)
