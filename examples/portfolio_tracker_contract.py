"""
Portfolio Tracker Intelligent Contract

Demonstrates portfolio valuation using the CoinGecko integration.
Shows how Intelligent Contracts can manage and report on
multi-asset cryptocurrency portfolios.
"""

from genlayer_integrations import CoinGeckoPriceFeed


class PortfolioTrackerContract:
    """
    Intelligent Contract for tracking cryptocurrency portfolio values.

    Accepts deposits of multiple assets and provides real-time
    portfolio valuation using external price data.
    """

    def __init__(self):
        self.feed = CoinGeckoPriceFeed()
        self.holdings: dict = {}  # coin_id -> amount
        self.owner: str = ""
        self.created_at: int = 0

    def initialize(self, owner_address: str):
        """Initialize the contract with an owner."""
        self.owner = owner_address
        self.created_at = __import__("time").time()

    def add_holding(self, coin_id: str, amount: float):
        """Add or update a holding in the portfolio."""
        if amount <= 0:
            return {"error": "Amount must be positive"}
        current = self.holdings.get(coin_id, 0.0)
        self.holdings[coin_id] = current + amount
        return {"coin": coin_id, "total_amount": self.holdings[coin_id]}

    def remove_holding(self, coin_id: str, amount: float):
        """Remove a holding from the portfolio."""
        current = self.holdings.get(coin_id, 0.0)
        if amount > current:
            return {"error": "Insufficient balance"}
        self.holdings[coin_id] = current - amount
        if self.holdings[coin_id] <= 0:
            del self.holdings[coin_id]
        return {"coin": coin_id, "remaining": self.holdings.get(coin_id, 0)}

    def get_portfolio_value(self, currency: str = "usd") -> dict:
        """Get the total value of the portfolio in the specified currency."""
        if not self.holdings:
            return {
                "total_value": 0.0,
                "holdings": {},
                "currency": currency,
                "message": "Portfolio is empty",
            }

        result = self.feed.get_portfolio_value(self.holdings, currency)

        # Add portfolio-level metadata
        result["asset_count"] = len(self.holdings)
        result["owner"] = self.owner

        # Calculate allocation percentages
        if result["total_value"] > 0:
            for coin_id, info in result["breakdown"].items():
                info["allocation_pct"] = round(
                    (info["value"] / result["total_value"]) * 100, 2
                )

        return result

    def get_asset_allocation(self) -> list:
        """Get the portfolio asset allocation breakdown."""
        if not self.holdings:
            return []

        result = self.feed.get_portfolio_value(self.holdings, "usd")
        allocation = []
        for coin_id, info in result["breakdown"].items():
            allocation.append({
                "coin": coin_id,
                "amount": info["amount"],
                "value_usd": round(info["value"], 2),
                "allocation_pct": info.get("allocation_pct", 0),
            })

        # Sort by allocation percentage descending
        allocation.sort(key=lambda x: x["allocation_pct"], reverse=True)
        return allocation
