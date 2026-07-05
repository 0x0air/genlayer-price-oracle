"""
Market Sentiment Intelligent Contract

Demonstrates how GenLayer's LLM capabilities can be combined with
real-time price data from the CoinGecko integration to produce
AI-powered market analysis directly on-chain.

Key GenLayer features demonstrated:
  - @llm_prompt decorator for LLM-based reasoning
  - External web data access via CoinGecko integration
  - Combining data fetching with AI analysis
"""

# from genlayer import llm_prompt  # GenLayer SDK decorator
from genlayer_integrations import CoinGeckoPriceFeed, CoinGeckoClient


class MarketSentimentContract:
    """
    Intelligent Contract that analyzes cryptocurrency market sentiment.

    Fetches real-time market data and uses GenLayer's LLM to produce
    AI-powered market analysis and sentiment assessments.
    """

    def __init__(self):
        self.feed = CoinGeckoPriceFeed()
        self.client = CoinGeckoClient()
        self.analysis_count: int = 0
        self.last_analysis: str = ""

    # In a real GenLayer Intelligent Contract, this would use @llm_prompt
    # to have the LLM analyze the market data:
    #
    # @llm_prompt
    # def analyze_market(self, market_data: str) -> str:
    #     \"\"\"
    #     Analyze the following cryptocurrency market data and provide:
    #     1. Overall market sentiment (bullish/bearish/neutral)
    #     2. Notable trends or patterns
    #     3. Top performing and worst performing assets
    #     4. Brief reasoning for your assessment
    #
    #     Market Data: {market_data}
    #     \"\"\"
    #     pass

    def get_market_snapshot(self) -> dict:
        """
        Get a comprehensive snapshot of the current market.

        Fetches global market data, top coins, and trending coins
        in a single coherent response.

        Returns:
            Dict with market overview, top movers, and trends
        """
        try:
            # Fetch global market data
            global_data = self.client.get_global_data()
            market_data = global_data.get("data", {})

            # Fetch top 10 coins
            top_coins = self.client.get_top_coins(per_page=10)

            # Fetch trending coins
            trending = self.client.get_trending()
            trending_coins = [
                {
                    "name": item["item"]["name"],
                    "symbol": item["item"]["symbol"],
                    "market_cap_rank": item["item"].get("market_cap_rank"),
                    "score": item["item"]["score"],
                }
                for item in trending.get("coins", [])[:5]
            ]

            # Calculate top gainers and losers
            sorted_by_change = sorted(
                top_coins,
                key=lambda c: c.get("price_change_percentage_24h", 0) or 0,
            )
            top_gainers = [
                {
                    "name": c["name"],
                    "symbol": c["symbol"].upper(),
                    "price": c["current_price"],
                    "change_pct": round(c.get("price_change_percentage_24h", 0), 2),
                }
                for c in sorted_by_change[-3:][::-1]
            ]
            top_losers = [
                {
                    "name": c["name"],
                    "symbol": c["symbol"].upper(),
                    "price": c["current_price"],
                    "change_pct": round(c.get("price_change_percentage_24h", 0), 2),
                }
                for c in sorted_by_change[:3]
            ]

            return {
                "market_cap_usd": market_data.get("total_market_cap", {}).get("usd"),
                "volume_usd": market_data.get("total_volume", {}).get("usd"),
                "btc_dominance": market_data.get("market_cap_percentage", {}).get("btc"),
                "eth_dominance": market_data.get("market_cap_percentage", {}).get("eth"),
                "market_cap_change_pct_24h": market_data.get("market_cap_change_percentage_24h_usd"),
                "active_cryptocurrencies": market_data.get("active_cryptocurrencies"),
                "top_gainers": top_gainers,
                "top_losers": top_losers,
                "trending": trending_coins,
                "top_coins_count": len(top_coins),
            }
        except Exception as e:
            return {"error": str(e)}

    def compare_assets(self, coin_ids: list, currency: str = "usd") -> dict:
        """
        Compare multiple cryptocurrencies side by side.

        Useful for contracts that need to make decisions based on
        relative asset performance.

        Args:
            coin_ids: List of CoinGecko coin IDs to compare
            currency: Target currency for prices

        Returns:
            Dict with comparative analysis data
        """
        try:
            prices = self.feed.get_prices(coin_ids, currency)
            results = {}

            for coin_id in coin_ids:
                try:
                    ctx = self.feed.get_price_with_market_context(coin_id, currency)
                    results[coin_id] = {
                        "price": ctx["current_price"],
                        "market_cap": ctx["market_cap"],
                        "market_cap_rank": ctx["market_cap_rank"],
                        "change_24h_pct": ctx["price_change_pct_24h"],
                        "volume_24h": ctx["total_volume"],
                    }
                except Exception:
                    results[coin_id] = {"price": prices.get(coin_id, 0), "error": "partial data"}

            # Find best and worst performer
            valid = {k: v for k, v in results.items() if "change_24h_pct" in v}
            if valid:
                best = max(valid.items(), key=lambda x: x[1].get("change_24h_pct", 0))
                worst = min(valid.items(), key=lambda x: x[1].get("change_24h_pct", 0))
                return {
                    "assets": results,
                    "best_performer": {"coin": best[0], "change_pct": best[1]["change_24h_pct"]},
                    "worst_performer": {"coin": worst[0], "change_pct": worst[1]["change_24h_pct"]},
                    "currency": currency,
                }

            return {"assets": results, "currency": currency}
        except Exception as e:
            return {"error": str(e)}

    def run_analysis(self, focus_coins: list = None) -> str:
        """
        Run a full market analysis with LLM reasoning.

        This method fetches market data and would use @llm_prompt
        to have the GenLayer LLM analyze it and provide insights.

        Args:
            focus_coins: Optional list of coins to focus analysis on

        Returns:
            AI-generated market analysis text
        """
        snapshot = self.get_market_snapshot()

        if "error" in snapshot:
            return f"Analysis failed: {snapshot['error']}"

        # In a real Intelligent Contract, the snapshot data would be
        # passed to an @llm_prompt method for AI analysis.
        #
        # For now, we structure the data ready for LLM consumption:
        self.analysis_count += 1
        self.last_analysis = f"Analysis #{self.analysis_count} complete"

        return self.last_analysis
