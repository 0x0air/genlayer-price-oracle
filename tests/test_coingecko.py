"""
Tests for the CoinGecko integration library.

Run with:
    pip install -e .
    python -m pytest tests/ -v

Or without pytest:
    python tests/test_coingecko.py
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestCoinGeckoClient(unittest.TestCase):
    """Tests for CoinGeckoClient."""

    def setUp(self):
        from genlayer_integrations import CoinGeckoClient
        self.client = CoinGeckoClient()

    def test_init_defaults(self):
        """Test default initialization."""
        self.assertEqual(self.client.BASE_URL, "https://api.coingecko.com/api/v3")
        self.assertIsNone(self.client._api_key)
        self.assertEqual(self.client._timeout, 15)

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = CoinGeckoClient(api_key="test_key", timeout=30)
        self.assertEqual(client._api_key, "test_key")
        self.assertEqual(client._timeout, 30)

    @patch("genlayer_integrations.base.urlopen")
    def test_get_simple_price_single(self, mock_urlopen):
        """Test getting price for a single coin."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"bitcoin": {"usd": 65432.10}}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.client.get_simple_price("bitcoin", "usd")
        self.assertEqual(result["bitcoin"]["usd"], 65432.10)

    @patch("genlayer_integrations.base.urlopen")
    def test_get_simple_price_multi(self, mock_urlopen):
        """Test getting prices for multiple coins."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"bitcoin": {"usd": 65432.10}, "ethereum": {"usd": 3456.78}}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.client.get_simple_price(
            ["bitcoin", "ethereum"], ["usd", "eur"]
        )
        self.assertIn("bitcoin", result)
        self.assertIn("ethereum", result)

    @patch("genlayer_integrations.coingecko.CoinGeckoClient.get_simple_price")
    def test_get_prices_batch(self, mock_get_price):
        """Test batch price fetching."""
        mock_get_price.return_value = {
            "bitcoin": {"usd": 65432.10},
            "ethereum": {"usd": 3456.78},
        }
        prices = self.client.get_prices_batch(
            ["bitcoin", "ethereum"], "usd"
        )
        self.assertEqual(prices["bitcoin"], 65432.10)
        self.assertEqual(prices["ethereum"], 3456.78)

    @patch("genlayer_integrations.base.urlopen")
    def test_get_trending(self, mock_urlopen):
        """Test getting trending coins."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"coins": [{"item": {"id": "test-coin", "name": "Test Coin", "symbol": "TEST", "market_cap_rank": 100, "score": 0}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.client.get_trending()
        self.assertIn("coins", result)
        self.assertEqual(result["coins"][0]["item"]["name"], "Test Coin")

    @patch("genlayer_integrations.base.urlopen")
    def test_get_global_data(self, mock_urlopen):
        """Test getting global market data."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"data": {"active_cryptocurrencies": 10000, "total_market_cap": {"usd": 2000000000000}}}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.client.get_global_data()
        self.assertIn("data", result)
        self.assertEqual(result["data"]["active_cryptocurrencies"], 10000)


class TestCoinGeckoPriceFeed(unittest.TestCase):
    """Tests for CoinGeckoPriceFeed."""

    def setUp(self):
        from genlayer_integrations import CoinGeckoPriceFeed
        self.feed = CoinGeckoPriceFeed()

    @patch("genlayer_integrations.coingecko.CoinGeckoClient.get_prices_batch")
    def test_get_price(self, mock_get_prices):
        """Test getting a single price."""
        mock_get_prices.return_value = {"bitcoin": 65432.10}
        price = self.feed.get_price("bitcoin")
        self.assertEqual(price, 65432.10)

    @patch("genlayer_integrations.coingecko.CoinGeckoClient.get_prices_batch")
    def test_get_prices(self, mock_get_prices):
        """Test getting multiple prices."""
        mock_get_prices.return_value = {
            "bitcoin": 65432.10,
            "ethereum": 3456.78,
        }
        prices = self.feed.get_prices(["bitcoin", "ethereum"])
        self.assertEqual(len(prices), 2)

    @patch("genlayer_integrations.coingecko.CoinGeckoPriceFeed.get_prices")
    def test_get_portfolio_value(self, mock_get_prices):
        """Test portfolio valuation."""
        mock_get_prices.return_value = {"bitcoin": 50000.0, "ethereum": 3000.0}

        result = self.feed.get_portfolio_value({
            "bitcoin": 0.5,
            "ethereum": 2.0,
        })

        self.assertIn("total_value", result)
        self.assertIn("breakdown", result)
        expected_total = (0.5 * 50000) + (2.0 * 3000)
        self.assertEqual(result["total_value"], expected_total)

    def test_empty_portfolio(self):
        """Test portfolio valuation with empty holdings."""
        result = self.feed.get_portfolio_value({})
        self.assertEqual(result["total_value"], 0.0)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling."""

    def setUp(self):
        from genlayer_integrations import CoinGeckoClient
        self.client = CoinGeckoClient()

    @patch("genlayer_integrations.base.urlopen")
    def test_rate_limit_handling(self, mock_urlopen):
        """Test that rate limits raise proper exception."""
        from urllib.error import HTTPError
        from genlayer_integrations.exceptions import APIRateLimitError

        mock_urlopen.side_effect = HTTPError(
            url="/simple/price", code=429, msg="Too Many Requests",
            hdrs={}, fp=None
        )

        with self.assertRaises(APIRateLimitError):
            self.client.get_simple_price("bitcoin", "usd")


if __name__ == "__main__":
    unittest.main()
