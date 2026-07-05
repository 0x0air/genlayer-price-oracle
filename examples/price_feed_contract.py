"""
Price Feed Intelligent Contract

A GenLayer Intelligent Contract that uses the CoinGecko integration
to provide real-time cryptocurrency price data on-chain.

This contract demonstrates how to:
  1. Import and use the CoinGecko integration library
  2. Expose price data as a contract read method
  3. Use LLM reasoning to analyze price movements

Deploy with:
  genlayer contract deploy examples/price_feed_contract.py
"""

# In a real GenLayer Intelligent Contract, the import would be:
# from genlayer_integrations import CoinGeckoPriceFeed
#
# For development/testing outside GenLayer, the library can be
# installed via: pip install genlayer-price-oracle

from genlayer_integrations import CoinGeckoPriceFeed, CoinGeckoClient
from genlayer_integrations.exceptions import (
    IntegrationError,
    APIRateLimitError,
)


class PriceFeedContract:
    """
    GenLayer Intelligent Contract for cryptocurrency price feeds.

    Provides on-chain access to real-time cryptocurrency prices
    via the CoinGecko API. Supports single and batch price queries.
    """

    def __init__(self):
        # Initialize the price feed
        self.feed = CoinGeckoPriceFeed()
        self.client = CoinGeckoClient()

        # Contract storage (typed)
        self.last_update: int = 0
        self.last_price: float = 0.0
        self.last_coin: str = ""

    def get_price(self, coin_id: str, currency: str = "usd") -> float:
        """
        Get the current price of a cryptocurrency.

        This is a read-only method that can be called by other
        contracts or external users.

        Args:
            coin_id: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
            currency: Target currency (e.g., "usd", "eur")

        Returns:
            Current price as a float
        """
        try:
            price = self.feed.get_price(coin_id, currency)
            return price
        except APIRateLimitError:
            # Return last known price if rate limited
            if self.last_coin == coin_id:
                return self.last_price
            raise
        except IntegrationError:
            raise

    def get_prices_batch(self, coin_ids: list, currency: str = "usd") -> dict:
        """
        Get prices for multiple cryptocurrencies in one call.

        Args:
            coin_ids: List of CoinGecko coin IDs
            currency: Target currency

        Returns:
            Dict mapping coin_id to price
        """
        try:
            prices = self.feed.get_prices(coin_ids, currency)
            return prices
        except IntegrationError as e:
            return {"error": str(e)}

    def get_price_with_context(self, coin_id: str, currency: str = "usd") -> dict:
        """
        Get enriched price data with market context.

        Returns not just the price but also 24h changes, high/low,
        market cap, and other context useful for LLM reasoning.
        """
        try:
            ctx = self.feed.get_price_with_market_context(coin_id, currency)
            return ctx
        except IntegrationError as e:
            return {"error": str(e)}

    def update_price(self, coin_id: str, currency: str = "usd") -> float:
        """
        Update and store the latest price for a coin.

        This is a write method that updates the contract state.
        """
        price = self.get_price(coin_id, currency)
        self.last_price = price
        self.last_coin = coin_id
        self.last_update = __import__("time").time()
        return price

    def get_top_movers(self, direction: str = "gainers", count: int = 5) -> list:
        """
        Get top gaining or losing cryptocurrencies.

        Args:
            direction: "gainers" or "losers"
            count: Number of coins to return (max 20)

        Returns:
            List of coin data dicts with name, price, and change percentage
        """
        try:
            coins = self.client.get_top_coins(
                vs_currency="usd",
                per_page=min(count * 3, 250),  # Fetch extra for filtering
                order="volume_desc",
            )

            # Sort by 24h change
            sorted_coins = sorted(
                coins,
                key=lambda c: c.get("price_change_percentage_24h", 0) or 0,
                reverse=(direction == "gainers"),
            )

            return [
                {
                    "name": c["name"],
                    "symbol": c["symbol"].upper(),
                    "price": c["current_price"],
                    "change_pct": c.get("price_change_percentage_24h", 0),
                    "market_cap_rank": c.get("market_cap_rank"),
                }
                for c in sorted_coins[:count]
            ]
        except IntegrationError as e:
            return [{"error": str(e)}]
