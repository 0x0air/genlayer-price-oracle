# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import typing
import json


class PriceFeedContract(gl.Contract):
    """
    Intelligent Contract that fetches cryptocurrency prices from CoinGecko.

    This contract demonstrates how to:
      1. Access external REST APIs (CoinGecko) from an Intelligent Contract
      2. Use gl.eq_principle.strict_eq() for consensus on external data
      3. Store and expose price data as contract state
      4. Handle errors from external API calls

    Deploy with GenLayer CLI:
      genlayer contract deploy examples/price_feed_contract.py

    Usage:
      - Call fetch_price() to get the latest BTC price
      - Call show_price() to view stored price
      - Call fetch_multi_prices() to get multiple coins
    """

    last_price: f64
    last_coin: str
    last_currency: str
    last_timestamp: u256
    price_history: DynArray[tuple[u256, str, str, f64]]

    def __init__(self):
        self.last_price = f64(0)
        self.last_coin = ""
        self.last_currency = ""
        self.last_timestamp = u256(0)
        self.price_history = DynArray[tuple[u256, str, str, f64]]()

    @gl.public.view
    def show_price(self) -> str:
        """View the last fetched price."""
        if self.last_timestamp == u256(0):
            return "No price fetched yet. Call fetch_price() first."
        return (
            f"Coin: {self.last_coin}\n"
            f"Price: {self.last_price:.2f} {self.last_currency.upper()}\n"
            f"Updated: timestamp {self.last_timestamp}"
        )

    @gl.public.view
    def show_history(self, limit: u256 = u256(10)) -> str:
        """View recent price fetch history."""
        start = max(u256(0), u256(len(self.price_history)) - limit)
        result = "=== Price History ===\n"
        for i in range(start, len(self.price_history)):
            ts, coin, currency, price = self.price_history[i]
            result += f"[{ts}] {coin}: {price:.2f} {currency}\n"
        return result

    @gl.public.write
    def fetch_price(
        self,
        coin_id: str = "bitcoin",
        vs_currency: str = "usd",
    ) -> str:
        """
        Fetch the current price of a cryptocurrency from CoinGecko.

        This is a write method because it updates contract storage.
        The actual web request happens inside gl.eq_principle.strict_eq()
        to ensure all validators agree on the result.

        Args:
            coin_id: CoinGecko coin ID (e.g., "bitcoin", "ethereum")
            vs_currency: Target currency (e.g., "usd", "eur")

        Returns:
            A human-readable string with the price result
        """
        def fetch_from_coingecko() -> str:
            url = (
                f"https://api.coingecko.com/api/v3/simple/price"
                f"?ids={coin_id}&vs_currencies={vs_currency}"
            )
            response = gl.nondet.web.get(url)

            if response.status_code != 200:
                raise gl.UserError(
                    f"CoinGecko API returned HTTP {response.status_code}"
                )

            body_str = response.body.decode("utf-8")
            data = json.loads(body_str)

            if coin_id not in data:
                raise gl.UserError(f"Coin '{coin_id}' not found in CoinGecko response")

            price = data[coin_id][vs_currency]
            return f"{price}"

        try:
            price_str = gl.eq_principle.strict_eq(fetch_from_coingecko)
            price_val = f64(float(price_str))

            # Update contract state
            self.last_price = price_val
            self.last_coin = coin_id
            self.last_currency = vs_currency
            self.last_timestamp = u256(__import__("time").time())

            # Add to history
            self.price_history.append(
                (self.last_timestamp, coin_id, vs_currency, price_val)
            )

            return (
                f"✓ Fetched {coin_id}: {price_val:.2f} {vs_currency.upper()}"
            )

        except gl.UserError as e:
            return f"✗ Error: {e.message}"
        except Exception as e:
            return f"✗ Unexpected error: {str(e)}"

    @gl.public.write
    def fetch_multi_prices(
        self,
        coin_ids: str,
        vs_currency: str = "usd",
    ) -> str:
        """
        Fetch prices for multiple cryptocurrencies.

        Args:
            coin_ids: Comma-separated list of CoinGecko IDs (e.g., "bitcoin,ethereum,solana")
            vs_currency: Target currency

        Returns:
            Formatted string with all prices
        """
        def fetch_multi() -> str:
            url = (
                f"https://api.coingecko.com/api/v3/simple/price"
                f"?ids={coin_ids}&vs_currencies={vs_currency}"
            )
            response = gl.nondet.web.get(url)

            if response.status_code != 200:
                raise gl.UserError(
                    f"CoinGecko API returned HTTP {response.status_code}"
                )

            return response.body.decode("utf-8")

        try:
            data_str = gl.eq_principle.strict_eq(fetch_multi)
            data = json.loads(data_str)

            id_list = [c.strip() for c in coin_ids.split(",")]
            result = f"=== Multi-Price Fetch ({vs_currency.upper()}) ===\n"

            for coin_id in id_list:
                if coin_id in data:
                    price = data[coin_id][vs_currency]
                    result += f"  {coin_id}: {price:.2f}\n"
                else:
                    result += f"  {coin_id}: NOT FOUND\n"

            return result

        except gl.UserError as e:
            return f"✗ Error: {e.message}"
        except Exception as e:
            return f"✗ Unexpected error: {str(e)}"
