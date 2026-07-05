"""
CoinGecko API integration for GenLayer Intelligent Contracts.

Provides a clean interface for Intelligent Contracts to fetch
cryptocurrency price data, market data, and trends from CoinGecko.

Free tier (no API key required):
  - 10-30 calls/min
  - Current price data
  - Market data (top 250 coins)
  - Trending coins

Pro API key:
  - Higher rate limits
  - Historical data
  - More endpoints
"""

import json
from typing import Any, Dict, List, Optional, Union

from .base import BaseIntegration
from .exceptions import InvalidResponseError


class CoinGeckoClient(BaseIntegration):
    """
    CoinGecko API client for GenLayer Intelligent Contracts.

    This client wraps the CoinGecko public API (v3) and provides
    methods to fetch cryptocurrency prices, market data, and trends.
    It is designed to be used within GenLayer Intelligent Contracts.

    Basic usage:
        client = CoinGeckoClient()
        btc_price = client.get_simple_price(ids="bitcoin", vs_currencies="usd")

        eth_data = client.get_coin_data("ethereum")
        print(eth_data["market_data"]["current_price"]["usd"])
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    # ------------------------------------------------------------------
    # Simple Price Endpoints
    # ------------------------------------------------------------------

    def get_simple_price(
        self,
        ids: Union[str, List[str]],
        vs_currencies: Union[str, List[str]] = "usd",
        include_market_cap: bool = False,
        include_24hr_vol: bool = False,
        include_24hr_change: bool = False,
    ) -> Dict[str, Any]:
        """
        Get the current price of one or more cryptocurrencies.

        This is the most commonly used endpoint for Intelligent Contracts
        that need real-time price data.

        Args:
            ids: CoinGecko coin ID(s), e.g., "bitcoin" or ["bitcoin", "ethereum"]
            vs_currencies: Target currency(s), e.g., "usd" or ["usd", "eur"]
            include_market_cap: Include market cap in response
            include_24hr_vol: Include 24h volume
            include_24hr_change: Include 24h price change

        Returns:
            Dict mapping coin IDs to price data, e.g.:
            {"bitcoin": {"usd": 65432.10}}

        Example:
            >>> client = CoinGeckoClient()
            >>> client.get_simple_price("bitcoin", "usd")
            {"bitcoin": {"usd": 65432.10}}
        """
        params = {
            "ids": ",".join(ids) if isinstance(ids, list) else ids,
            "vs_currencies": ",".join(vs_currencies)
            if isinstance(vs_currencies, list)
            else vs_currencies,
        }
        if include_market_cap:
            params["include_market_cap"] = "true"
        if include_24hr_vol:
            params["include_24hr_vol"] = "true"
        if include_24hr_change:
            params["include_24hr_change"] = "true"

        data = self._request("/simple/price", params)
        self._validate_response(data)
        return data

    # ------------------------------------------------------------------
    # Coin Data Endpoints
    # ------------------------------------------------------------------

    def get_coin_data(
        self,
        coin_id: str,
        localization: bool = False,
        tickers: bool = False,
        market_data: bool = True,
        community_data: bool = False,
        developer_data: bool = False,
        sparkline: bool = False,
    ) -> Dict[str, Any]:
        """
        Get comprehensive data for a single cryptocurrency.

        Includes market data, description, links, and more.

        Args:
            coin_id: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
            localization: Include localized descriptions
            tickers: Include exchange tickers
            market_data: Include market statistics
            community_data: Include community stats
            developer_data: Include developer stats (GitHub, etc.)
            sparkline: Include 7-day price sparkline

        Returns:
            Comprehensive coin data dictionary

        Example:
            >>> client = CoinGeckoClient()
            >>> data = client.get_coin_data("bitcoin")
            >>> price = data["market_data"]["current_price"]["usd"]
        """
        params = {
            "localization": str(localization).lower(),
            "tickers": str(tickers).lower(),
            "market_data": str(market_data).lower(),
            "community_data": str(community_data).lower(),
            "developer_data": str(developer_data).lower(),
            "sparkline": str(sparkline).lower(),
        }
        data = self._request(f"/coins/{coin_id}", params)
        self._validate_response(data)
        return data

    def get_coin_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: Union[int, str] = 7,
    ) -> Dict[str, Any]:
        """
        Get historical price data for charting.

        Args:
            coin_id: CoinGecko coin ID
            vs_currency: Target currency
            days: Number of days of data (1, 7, 14, 30, 90, 180, 365, "max")

        Returns:
            Dict with "prices", "market_caps", "total_volumes" arrays.
            Each array contains [timestamp, value] pairs.

        Example:
            >>> client = CoinGeckoClient()
            >>> chart = client.get_coin_market_chart("bitcoin", "usd", 7)
            >>> latest_price = chart["prices"][-1][1]
        """
        data = self._request(f"/coins/{coin_id}/market_chart", {
            "vs_currency": vs_currency,
            "days": str(days),
        })
        self._validate_response(data)
        return data

    # ------------------------------------------------------------------
    # Market Data Endpoints
    # ------------------------------------------------------------------

    def get_top_coins(
        self,
        vs_currency: str = "usd",
        category: str = "",
        order: str = "market_cap_desc",
        per_page: int = 50,
        page: int = 1,
        sparkline: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get top cryptocurrencies by market cap.

        Args:
            vs_currency: Target currency for prices
            category: Filter by category (e.g., "decentralized-finance-defi")
            order: Sort order (market_cap_desc, volume_desc, id_asc, etc.)
            per_page: Results per page (max 250)
            page: Page number
            sparkline: Include 7-day sparkline

        Returns:
            List of coin market data dictionaries

        Example:
            >>> client = CoinGeckoClient()
            >>> top_10 = client.get_top_coins(per_page=10)
            >>> for coin in top_10:
            ...     print(coin["name"], coin["current_price"])
        """
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": str(per_page),
            "page": str(page),
            "sparkline": str(sparkline).lower(),
        }
        if category:
            params["category"] = category

        data = self._request("/coins/markets", params)
        self._validate_response(data)
        return data

    # ------------------------------------------------------------------
    # Trending Endpoints
    # ------------------------------------------------------------------

    def get_trending(self) -> Dict[str, Any]:
        """
        Get trending cryptocurrencies on CoinGecko.

        Useful for Intelligent Contracts that need to identify
        market trends and popular coins.

        Returns:
            Dict with "coins" list containing trending coin data

        Example:
            >>> client = CoinGeckoClient()
            >>> trending = client.get_trending()
            >>> for item in trending["coins"][:5]:
            ...     coin = item["item"]
            ...     print(coin["name"], coin["symbol"], coin["market_cap_rank"])
        """
        data = self._request("/search/trending")
        self._validate_response(data)
        return data

    # ------------------------------------------------------------------
    # Global & Exchange Data
    # ------------------------------------------------------------------

    def get_global_data(self) -> Dict[str, Any]:
        """
        Get global cryptocurrency market statistics.

        Returns total market cap, BTC dominance, trading volume, etc.

        Returns:
            Dict with global market data under "data" key

        Example:
            >>> client = CoinGeckoClient()
            >>> global_data = client.get_global_data()
            >>> total_mcap = global_data["data"]["total_market_cap"]["usd"]
            >>> btc_dominance = global_data["data"]["market_cap_percentage"]["btc"]
        """
        data = self._request("/global")
        self._validate_response(data)
        return data

    def get_exchange_rates(self) -> Dict[str, Any]:
        """
        Get current BTC-to-fiat exchange rates.

        Returns:
            Dict with exchange rates under "rates" key

        Example:
            >>> client = CoinGeckoClient()
            >>> rates = client.get_exchange_rates()
            >>> usd_rate = rates["rates"]["usd"]
        """
        data = self._request("/exchange_rates")
        self._validate_response(data)
        return data

    # ------------------------------------------------------------------
    # Batch & Convenience Methods
    # ------------------------------------------------------------------

    def get_prices_batch(
        self, coin_ids: List[str], vs_currency: str = "usd"
    ) -> Dict[str, float]:
        """
        Get prices for multiple coins in one call.

        This is the recommended method for Intelligent Contracts that
        need to check prices of multiple assets.

        Args:
            coin_ids: List of CoinGecko coin IDs
            vs_currency: Target currency

        Returns:
            Dict mapping coin_id to price, e.g.:
            {"bitcoin": 65432.10, "ethereum": 3456.78}

        Example:
            >>> client = CoinGeckoClient()
            >>> prices = client.get_prices_batch(
            ...     ["bitcoin", "ethereum", "solana"],
            ...     "usd"
            ... )
        """
        raw = self.get_simple_price(
            ids=coin_ids, vs_currencies=vs_currency
        )
        return {
            coin_id: data[vs_currency]
            for coin_id, data in raw.items()
        }

    def get_price_with_change(
        self, coin_id: str, vs_currency: str = "usd"
    ) -> Dict[str, float]:
        """
        Get price plus 24h change for a single coin.

        Args:
            coin_id: CoinGecko coin ID
            vs_currency: Target currency

        Returns:
            Dict with "price", "change_24h", and "change_pct" keys

        Example:
            >>> client = CoinGeckoClient()
            >>> info = client.get_price_with_change("bitcoin")
            >>> if info["change_pct"] > 5:
            ...     # significant price movement detected
        """
        raw = self.get_simple_price(
            ids=coin_id,
            vs_currencies=vs_currency,
            include_24hr_change=True,
        )
        coin_data = raw.get(coin_id, {})
        return {
            "price": coin_data.get(vs_currency, 0.0),
            "change_24h": coin_data.get(f"{vs_currency}_24h_change", 0.0),
            "change_pct": coin_data.get(
                f"{vs_currency}_24h_change", 0.0
            ),
        }


class CoinGeckoPriceFeed:
    """
    High-level price feed abstraction for Intelligent Contracts.

    Provides a simplified interface for contracts that just need
    reliable price data with caching and fallback logic.

    Usage in a GenLayer Intelligent Contract:
        feed = CoinGeckoPriceFeed()
        btc_usd = feed.get_price("bitcoin")
        eth_usd = feed.get_price("ethereum")
        portfolio_value = feed.get_portfolio_value({
            "bitcoin": 0.5,
            "ethereum": 2.0,
            "solana": 10.0,
        })
    """

    def __init__(self, api_key: Optional[str] = None):
        self._client = CoinGeckoClient(api_key=api_key)

    def get_price(self, coin_id: str, vs_currency: str = "usd") -> float:
        """
        Get the current price of a single coin.

        Args:
            coin_id: CoinGecko coin ID
            vs_currency: Target currency

        Returns:
            Current price as float

        Example:
            >>> feed = CoinGeckoPriceFeed()
            >>> feed.get_price("bitcoin")
            65432.10
        """
        prices = self._client.get_prices_batch([coin_id], vs_currency)
        return prices.get(coin_id, 0.0)

    def get_prices(self, coin_ids: List[str], vs_currency: str = "usd") -> Dict[str, float]:
        """
        Get prices for multiple coins.

        Args:
            coin_ids: List of CoinGecko coin IDs
            vs_currency: Target currency

        Returns:
            Dict mapping coin_id to price
        """
        return self._client.get_prices_batch(coin_ids, vs_currency)

    def get_portfolio_value(
        self,
        holdings: Dict[str, float],
        vs_currency: str = "usd",
    ) -> Dict[str, Any]:
        """
        Calculate the total value of a cryptocurrency portfolio.

        Args:
            holdings: Dict mapping coin_id to amount held
            vs_currency: Target currency for valuation

        Returns:
            Dict with:
              - total_value: Sum of all holdings in vs_currency
              - breakdown: Per-coin value breakdown
              - prices: Current prices used

        Example:
            >>> feed = CoinGeckoPriceFeed()
            >>> result = feed.get_portfolio_value({
            ...     "bitcoin": 0.5,
            ...     "ethereum": 2.0,
            ... })
            >>> result["total_value"]
            39234.56
        """
        coin_ids = list(holdings.keys())
        prices = self.get_prices(coin_ids, vs_currency)

        breakdown = {}
        total = 0.0
        for coin_id, amount in holdings.items():
            price = prices.get(coin_id, 0.0)
            value = amount * price
            breakdown[coin_id] = {
                "amount": amount,
                "price": price,
                "value": value,
            }
            total += value

        return {
            "total_value": round(total, 2),
            "breakdown": breakdown,
            "prices": prices,
            "currency": vs_currency,
        }

    def get_price_with_market_context(
        self, coin_id: str, vs_currency: str = "usd"
    ) -> Dict[str, Any]:
        """
        Get price with additional market context for AI reasoning.

        Returns price data enriched with market metrics that can be
        used by GenLayer's @llm_prompt for intelligent analysis.

        Args:
            coin_id: CoinGecko coin ID
            vs_currency: Target currency

        Returns:
            Dict with price, 24h change, and market context
        """
        coin_data = self._client.get_coin_data(
            coin_id, market_data=True, sparkline=True
        )
        md = coin_data.get("market_data", {})

        return {
            "coin_id": coin_id,
            "name": coin_data.get("name", ""),
            "symbol": coin_data.get("symbol", ""),
            "current_price": md.get("current_price", {}).get(vs_currency, 0),
            "market_cap": md.get("market_cap", {}).get(vs_currency, 0),
            "market_cap_rank": coin_data.get("market_cap_rank", 0),
            "price_change_24h": md.get("price_change_24h", 0),
            "price_change_pct_24h": md.get("price_change_percentage_24h", 0),
            "high_24h": md.get("high_24h", {}).get(vs_currency, 0),
            "low_24h": md.get("low_24h", {}).get(vs_currency, 0),
            "total_volume": md.get("total_volume", {}).get(vs_currency, 0),
            "circulating_supply": md.get("circulating_supply", 0),
            "total_supply": md.get("total_supply", 0),
            "ath": md.get("ath", {}).get(vs_currency, 0),
            "ath_change_pct": md.get("ath_change_percentage", {}).get(vs_currency, 0),
        }
