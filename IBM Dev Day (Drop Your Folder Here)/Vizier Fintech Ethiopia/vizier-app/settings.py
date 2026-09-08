"""Runtime configuration for the Vizier prototype."""

from __future__ import annotations

import os


COUNTRY = os.environ.get("VIZIER_COUNTRY", "Ethiopia")
CURRENCY = os.environ.get("VIZIER_CURRENCY", "ETB")
ENVIRONMENT = os.environ.get("VIZIER_ENV", "development").lower()
DEFAULT_STORAGE_SECRET = "vizier-local-development-secret"


def money(value: float, decimals: int = 0) -> str:
    return f"{'−' if value < 0 else ''}{CURRENCY} {abs(value):,.{decimals}f}"


def validate_runtime() -> str:
    secret = os.environ.get("VIZIER_STORAGE_SECRET", DEFAULT_STORAGE_SECRET)
    if ENVIRONMENT == "production":
        if secret == DEFAULT_STORAGE_SECRET or len(secret) < 32:
            raise RuntimeError(
                "VIZIER_STORAGE_SECRET must be a unique value of at least 32 characters in production."
            )
        if os.environ.get("VIZIER_ALLOW_DEMO_MARKET", "0") == "1":
            raise RuntimeError("Demo market data cannot be enabled in production.")
    return secret
