# GenLayer Price Oracle — CoinGecko Integration

A **third-party integration library** for [GenLayer](https://genlayer.com) Intelligent Contracts, providing a clean, well-documented interface to fetch real-time cryptocurrency price data from the **CoinGecko API**.

## 🎯 Purpose

This library lets Intelligent Contracts easily access external price data **without oracles or intermediaries**. Designed for the **"3rd party integrations"** contribution type on the GenLayer Portal.

### What it enables

| Use Case | Example |
|----------|---------|
| **Price Feeds** | Get BTC/USD price on-chain for DeFi contracts |
| **Portfolio Valuation** | Calculate total value of multi-asset holdings |
| **Market Analysis** | Identify top gainers/losers with LLM reasoning |
| **Trading Decisions** | Compare assets and detect trends |

## 📦 Project Structure

```
genlayer-price-oracle/
├── src/
│   └── genlayer_integrations/
│       ├── __init__.py          # Public API exports
│       ├── base.py              # Base HTTP client with error handling
│       ├── coingecko.py         # CoinGecko API wrapper + PriceFeed
│       └── exceptions.py        # Custom exception classes
├── examples/
│   ├── price_feed_contract.py           # Basic price feed contract
│   ├── market_sentiment_contract.py     # AI-powered market analysis
│   └── portfolio_tracker_contract.py    # Portfolio tracking contract
├── tests/
│   └── test_coingecko.py        # Unit tests (mock-based)
├── setup.py
└── README.md
```

## 🚀 Quick Start

### 1. Install

```bash
pip install -e .
```

### 2. Use in Python scripts (for testing)

```python
from genlayer_integrations import CoinGeckoPriceFeed

feed = CoinGeckoPriceFeed()

# Get a single price
btc_price = feed.get_price("bitcoin", "usd")
print(f"Bitcoin: ${btc_price}")

# Get multiple prices
prices = feed.get_prices(["bitcoin", "ethereum", "solana"])
print(prices)

# Value a portfolio
portfolio = feed.get_portfolio_value({
    "bitcoin": 0.5,
    "ethereum": 2.0,
})
print(f"Total value: ${portfolio['total_value']}")
```

### 3. Deploy as a GenLayer Intelligent Contract

```bash
# Using GenLayer CLI
genlayer contract deploy examples/price_feed_contract.py

# Read price data
genlayer contract call <contract_address> get_price bitcoin usd
```

## 📋 API Reference

### `CoinGeckoClient(urlopen)`

Low-level client wrapping the CoinGecko API v3.

| Method | Description |
|--------|-------------|
| `get_simple_price(ids, vs_currencies)` | Current price of 1+ coins |
| `get_coin_data(coin_id)` | Full coin data (market, description, etc.) |
| `get_coin_market_chart(coin_id, days)` | Historical price data for charting |
| `get_top_coins(per_page)` | Top coins by market cap |
| `get_trending()` | Currently trending coins |
| `get_global_data()` | Global market statistics |
| `get_exchange_rates()` | BTC exchange rates |
| `get_prices_batch(coin_ids)` | Batch price fetch (convenience) |
| `get_price_with_change(coin_id)` | Price + 24h change |

### `CoinGeckoPriceFeed(urlopen)`

High-level abstraction for Intelligent Contracts.

| Method | Description |
|--------|-------------|
| `get_price(coin_id, vs_currency)` | Simple price lookup |
| `get_prices(coin_ids, vs_currency)` | Multi-coin price lookup |
| `get_portfolio_value(holdings, vs_currency)` | Portfolio valuation |
| `get_price_with_market_context(coin_id)` | Enriched data for LLM analysis |

### Error Handling

| Exception | When |
|-----------|------|
| `APIRateLimitError` | Rate limited (HTTP 429) — use last known price |
| `InvalidResponseError` | Malformed API response |
| `IntegrationError` | Connection or HTTP errors |

## 🧪 Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

Or without pytest:

```bash
python tests/test_coingecko.py
```

## 🔌 Extending for Other APIs

The library is designed to be extensible. To add a new integration:

1. Create a new module (e.g., `weather.py`)
2. Inherit from `BaseIntegration`
3. Set `BASE_URL` and implement API-specific methods

```python
from genlayer_integrations.base import BaseIntegration

class OpenWeatherMap(BaseIntegration):
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def get_weather(self, city: str):
        return self._request("/weather", {
            "q": city,
            "appid": self._api_key,
        })
```

## 📄 License

MIT
