"""Optional market quote retrieval with explicit cache and demo fallback."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen

from investments import STOCKS


MARKET_PUBLIC_URL = os.environ.get("VIZIER_MARKET_URL", "")
CACHE_SECONDS = 300
_cache: dict[str, Any] = {"quotes": {}, "fetched_at": None}


def _ticker(symbol_name: str, issuer: str) -> str:
    ticker = symbol_name or issuer
    for suffix in (".O0000", ".E0000"):
        ticker = ticker.replace(suffix, "")
    return ticker.strip().upper()


def _parse_quotes(payload: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    quotes = {}
    for item in payload:
        ticker = _ticker(str(item.get("SymbolName") or ""), str(item.get("Issuer") or ""))
        if not ticker or not isinstance(item.get("LastTradedPrice"), (int, float)):
            continue
        quotes[ticker] = {
            "ticker": ticker, "issuer": item.get("CompanyDescription") or item.get("Issuer") or ticker,
            "price": float(item["LastTradedPrice"]), "change": float(item.get("Change") or 0),
            "change_pct": float(item.get("ChangePercentage") or 0), "open": float(item.get("OpenPrice") or 0),
            "high": float(item.get("HighestPrice") or 0), "low": float(item.get("LowestPrice") or 0),
            "volume": int(item.get("VolumeTraded") or 0), "trades": int(item.get("NumberOfTrades") or 0),
            "market_cap": float(item.get("MarketCapitalization") or 0),
        }
    return quotes


def get_quotes(force: bool = False, timeout: int = 60) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    now = datetime.now(timezone.utc)
    fetched = _cache["fetched_at"]
    if not force and fetched and (now - fetched).total_seconds() < CACHE_SECONDS:
        return _cache["quotes"], {"source": "Configured public quote feed", "fetched_at": fetched, "cached": True, "live": True}
    try:
        if not MARKET_PUBLIC_URL:
            raise RuntimeError("No market feed is configured for the Ethiopia profile")
        request = Request(MARKET_PUBLIC_URL, headers={"User-Agent": "Vizier/1.0"})
        with urlopen(request, timeout=timeout) as response:
            quotes = _parse_quotes(json.loads(response.read().decode("utf-8")))
        if not quotes:
            raise ValueError("Quote feed returned no instruments")
        _cache.update({"quotes": quotes, "fetched_at": now})
        return quotes, {"source": "Configured public quote feed", "fetched_at": now, "cached": False, "live": True}
    except Exception as error:
        if _cache["quotes"]:
            return _cache["quotes"], {"source": "Cached public quotes", "fetched_at": _cache["fetched_at"], "cached": True, "live": True, "error": str(error)}
        fallback = {ticker: {"ticker": ticker, "issuer": ticker, "price": price, "change": 0.0,
                    "change_pct": 0.0, "open": price, "high": price, "low": price,
                    "volume": 0, "trades": 0, "market_cap": 0.0} for ticker, price in STOCKS.items()}
        return fallback, {"source": "Demo fallback prices", "fetched_at": now, "cached": False, "live": False, "error": str(error)}
