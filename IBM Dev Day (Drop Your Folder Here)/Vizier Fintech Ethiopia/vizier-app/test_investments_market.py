import json
import unittest
from unittest.mock import patch

import market_data
from investments import calculate_portfolio


class PortfolioTests(unittest.TestCase):
    def test_portfolio_totals_dividends_and_allocation(self):
        holdings = [
            {"id": 1, "ticker": "ETH-TBILL", "shares": 100, "purchase_price": 20, "dividends": 100},
            {"id": 2, "ticker": "GOLD-GRAM", "shares": 10, "purchase_price": 50, "dividends": 0},
        ]
        quotes = {"ETH-TBILL": {"price": 25}, "GOLD-GRAM": {"price": 60}}
        result = calculate_portfolio(holdings, quotes)
        self.assertEqual(result["cost"], 2_500)
        self.assertEqual(result["value"], 3_100)
        self.assertEqual(result["gain"], 700)
        self.assertAlmostEqual(sum(row["allocation_pct"] for row in result["rows"]), 100)
        self.assertEqual(result["sectors"], 2)

    def test_missing_quote_uses_purchase_price(self):
        result = calculate_portfolio(
            [{"ticker": "TEST", "shares": 2, "purchase_price": 10, "dividends": 0}], {}
        )
        self.assertEqual(result["value"], 20)
        self.assertEqual(result["return_pct"], 0)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self): return json.dumps(self.payload).encode()


class MarketDataTests(unittest.TestCase):
    def setUp(self):
        market_data._cache = {"quotes": {}, "fetched_at": None}
        market_data.MARKET_PUBLIC_URL = "https://example.test/quotes"

    def test_public_quote_parsing_and_cache(self):
        payload = [{"SymbolName": "ETH-TBILL", "Issuer": "ETH-TBILL", "LastTradedPrice": 36.85,
                    "Change": .25, "ChangePercentage": .68, "OpenPrice": 36.5,
                    "HighestPrice": 37, "LowestPrice": 36, "VolumeTraded": 1000,
                    "NumberOfTrades": 20, "MarketCapitalization": 10_000}]
        with patch("market_data.urlopen", return_value=FakeResponse(payload)) as fetch:
            quotes, meta = market_data.get_quotes(force=True)
            cached, cached_meta = market_data.get_quotes()
        self.assertEqual(quotes["ETH-TBILL"]["price"], 36.85)
        self.assertTrue(meta["live"])
        self.assertTrue(cached_meta["cached"])
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(cached, quotes)

    def test_failed_feed_uses_demo_fallback(self):
        with patch("market_data.urlopen", side_effect=TimeoutError("offline")):
            quotes, meta = market_data.get_quotes(force=True)
        self.assertFalse(meta["live"])
        self.assertIn("ETH-TBILL", quotes)


if __name__ == "__main__":
    unittest.main()
