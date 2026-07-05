# GenLayer Price Oracle — CoinGecko Integration

A **third-party integration library** for [GenLayer](https://genlayer.com) Intelligent Contracts, providing a clean interface to fetch real-time cryptocurrency price data from **CoinGecko** directly on-chain — no oracles, no intermediaries.

> Built for the **"3rd party integrations"** contribution type on the [GenLayer Portal](https://portal.genlayer.foundation/validators/contributions).

---

## 📋 How It Works

This project contains two parts:

### 1. Python Library (`src/genlayer_integrations/`)

A reusable Python library for testing CoinGecko API interactions locally:

```python
from genlayer_integrations import CoinGeckoPriceFeed

feed = CoinGeckoPriceFeed()
btc_price = feed.get_price("bitcoin", "usd")
print(f"BTC: ${btc_price}")
```

### 2. GenLayer Intelligent Contracts (`examples/`)

Ready-to-deploy Intelligent Contracts that use `gl.nondet.web.get()` to fetch CoinGecko data on the GenLayer testnet.

---

## 🚀 Deploy to GenLayer Testnet

### Prerequisites

- [GenLayer CLI](https://docs.genlayer.com/api-references/genlayer-cli) installed
- An account with testnet funds (`genlayer account create`)

### Deploy the Price Feed Contract

```bash
# 1. Deploy
genlayer contract deploy examples/price_feed_contract.py

# 2. Fetch BTC price
genlayer contract call <CONTRACT_ADDRESS> fetch_price bitcoin usd

# 3. View stored price
genlayer contract call <CONTRACT_ADDRESS> show_price

# 4. Fetch multiple prices
genlayer contract call <CONTRACT_ADDRESS> fetch_multi_prices "bitcoin,ethereum,solana"
```

### Deploy the Market Overview Contract

```bash
genlayer contract deploy examples/market_overview_contract.py
genlayer contract call <ADDRESS> fetch_market_overview
genlayer contract call <ADDRESS> get_summary
```

---

## 🧪 Testing on Testnet

To test and validate that the contract works correctly on the GenLayer testnet:

```bash
# Deploy
genlayer contract deploy examples/price_feed_contract.py
# Example output:
# Contract deployed at: 0x1234...5678
# Transaction hash: 0xabcd...ef01

# Test 1: Fetch Bitcoin price
genlayer contract call 0x1234...5678 fetch_price bitcoin usd
# Expected: ✓ Fetched bitcoin: 65432.10 usd

# Test 2: Verify stored price
genlayer contract call 0x1234...5678 show_price
# Expected: Coin: bitcoin\nPrice: 65432.10 usd\nUpdated: timestamp XXXXXX

# Test 3: Multi-price fetch
genlayer contract call 0x1234...5678 fetch_multi_prices "bitcoin,ethereum"
# Expected: === Multi-Price Fetch (USD) ===\n  bitcoin: XXXXX\n  ethereum: XXXX

# Test 4: Check price history
genlayer contract call 0x1234...5678 show_history 5

# Test 5: Market overview
genlayer contract deploy examples/market_overview_contract.py
genlayer contract call <ADDRESS> fetch_market_overview
genlayer contract call <ADDRESS> get_summary
# Expected: Global Market Cap, BTC Dominance, Trending coins
```

---

## 📁 Project Structure

```
genlayer-price-oracle/
├── src/genlayer_integrations/
│   ├── __init__.py          # Public API exports
│   ├── base.py              # Base HTTP client
│   ├── coingecko.py         # CoinGecko wrapper + PriceFeed
│   └── exceptions.py        # Custom exceptions
├── examples/
│   ├── price_feed_contract.py       # Single/multi price fetch contract
│   └── market_overview_contract.py  # Global market stats + trending
├── tests/
│   └── test_coingecko.py    # Unit tests
├── setup.py
└── README.md
```

## 📡 API Reference (Python Library)

### CoinGeckoClient

| Method | Description |
|--------|-------------|
| `get_simple_price(ids, vs_currencies)` | Current price of any coin |
| `get_coin_data(coin_id)` | Full coin data (market, description) |
| `get_coin_market_chart(coin_id, days)` | Historical price data |
| `get_top_coins(per_page)` | Top N coins by market cap |
| `get_trending()` | Trending coins |
| `get_global_data()` | Global market stats |
| `get_prices_batch(coin_ids)` | Batch price fetch |

### CoinGeckoPriceFeed

| Method | Description |
|--------|-------------|
| `get_price(coin_id, vs_currency)` | Single price lookup |
| `get_prices(coin_ids, vs_currency)` | Multi-coin lookup |
| `get_portfolio_value(holdings, vs_currency)` | Portfolio valuation |
| `get_price_with_market_context(coin_id)` | Price + market data for LLM |

## 🔌 Extending

To add other API integrations (weather, social, AI), create a new module:

```python
from genlayer_integrations.base import BaseIntegration

class OpenWeatherMap(BaseIntegration):
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def get_weather(self, city: str):
        return self._request("/weather", {
            "q": city, "appid": self._api_key,
        })
```

## 🧪 Running Tests

```bash
pip install -e .
python -m pytest tests/ -v
```

## 📄 License

MIT
