# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import typing
import json


class MarketOverviewContract(gl.Contract):
    """
    Intelligent Contract that fetches market overview data from CoinGecko.

    Provides global crypto market statistics and trending coins.
    Demonstrates how to use multiple external API calls within
    a single Intelligent Contract.
    """

    last_global_mcap: f64
    last_btc_dominance: f64
    last_trending: str
    last_updated: u256

    def __init__(self):
        self.last_global_mcap = f64(0)
        self.last_btc_dominance = f64(0)
        self.last_trending = ""
        self.last_updated = u256(0)

    @gl.public.view
    def get_summary(self) -> str:
        """Get a summary of the last market overview."""
        if self.last_updated == u256(0):
            return "No data yet. Call fetch_market_overview() first."
        return (
            f"=== Market Overview ===\n"
            f"Global Market Cap: ${self.last_global_mcap:.2f}\n"
            f"BTC Dominance: {self.last_btc_dominance:.2f}%\n"
            f"Trending: {self.last_trending}\n"
            f"Last Updated: {self.last_updated}"
        )

    @gl.public.write
    def fetch_market_overview(self) -> str:
        """
        Fetch global cryptocurrency market data from CoinGecko.
        """
        def fetch_global() -> str:
            response = gl.nondet.web.get(
                "https://api.coingecko.com/api/v3/global"
            )
            if response.status_code != 200:
                raise gl.UserError(f"API error: {response.status_code}")
            return response.body.decode("utf-8")

        def fetch_trending() -> str:
            response = gl.nondet.web.get(
                "https://api.coingecko.com/api/v3/search/trending"
            )
            if response.status_code != 200:
                return "[]"
            return response.body.decode("utf-8")

        try:
            global_str = gl.eq_principle.strict_eq(fetch_global)
            trending_str = gl.eq_principle.strict_eq(fetch_trending)

            global_data = json.loads(global_str)
            market_data = global_data.get("data", {})

            mcap = market_data.get("total_market_cap", {}).get("usd", 0)
            btc_dom = market_data.get("market_cap_percentage", {}).get("btc", 0)

            # Parse trending
            trending_data = json.loads(trending_str)
            trending_coins = trending_data.get("coins", [])[:5]
            trending_names = ", ".join(
                c["item"]["name"] for c in trending_coins
            ) or "None"

            self.last_global_mcap = f64(mcap)
            self.last_btc_dominance = f64(btc_dom)
            self.last_trending = trending_names
            self.last_updated = u256(__import__("time").time())

            return (
                f"✓ Market overview updated!\n"
                f"  Total Market Cap: ${mcap:,.0f}\n"
                f"  BTC Dominance: {btc_dom:.2f}%\n"
                f"  Trending: {trending_names}"
            )

        except gl.UserError as e:
            return f"✗ Error: {e.message}"
        except Exception as e:
            return f"✗ Unexpected error: {str(e)}"
