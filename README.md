# GenLayer Price Oracle — CoinGecko Integration

A Python library + Intelligent Contracts for fetching real-time cryptocurrency prices from CoinGecko on GenLayer. No oracles. No intermediaries. Just `gl.nondet.web.get()` and CoinGecko public API.

---

## What's inside

Two parts that work together:

**`src/genlayer_integrations/`** — reusable Python library, useful for testing the CoinGecko API locally:

```python
from genlayer_integrations import CoinGeckoPriceFeed

feed = CoinGeckoPriceFeed()
btc = feed.get_price("bitcoin", "usd")
print(f"BTC: ${btc}")
```

**`examples/`** — ready-to-deploy Intelligent Contracts, written in proper genlayer format. These are what you actually put on-chain.

---

## Deploy to Testnet

### Prerequisites

- [GenLayer CLI](https://docs.genlayer.com/api-references/genlayer-cli) installed & `genlayer init` done
- An account with testnet funds (`genlayer account create` → faucet at https://testnet-faucet.genlayer.foundation)
- Network set to Bradbury (`genlayer network set bradbury`)

### Price Feed Contract

```bash
genlayer deploy --contract examples/price_feed_contract.py

# Read — no gas
genlayer call <CONTRACT> show_price

# Write — fetches live price from CoinGecko, stores it on-chain
genlayer write <CONTRACT> fetch_price bitcoin usd

# Multi-coin
genlayer write <CONTRACT> fetch_multi_prices "bitcoin,ethereum,solana"

# History
genlayer call <CONTRACT> show_history 5
```

### Market Overview Contract

```bash
genlayer deploy --contract examples/market_overview_contract.py
genlayer write <CONTRACT> fetch_market_overview
genlayer call <CONTRACT> get_summary
```

---

## Quick test flow

```bash
# Deploy
genlayer deploy --contract examples/price_feed_contract.py
# → Contract deployed at: 0x1234...5678

# Fetch BTC price
genlayer write 0x1234...5678 fetch_price bitcoin usd
# → ✓ Fetched bitcoin: 65432.10 usd

# Check stored state
genlayer call 0x1234...5678 show_price
# → Coin: bitcoin
#   Price: 65432.10 usd
#   Updated: timestamp XXXXXX

# Multi-price
genlayer write 0x1234...5678 fetch_multi_prices "bitcoin,ethereum"
# → === Multi-Price Fetch (USD) ===
#     bitcoin: 65432.10
#     ethereum: 3456.78

# Market overview
genlayer deploy --contract examples/market_overview_contract.py
genlayer write <ADDRESS> fetch_market_overview
genlayer call <ADDRESS> get_summary
# → Market cap, BTC dominance, trending coins
```

---

## Project layout

```
genlayer-price-oracle/
├── src/genlayer_integrations/
│   ├── __init__.py
│   ├── base.py
│   ├── coingecko.py
│   └── exceptions.py
├── examples/
│   ├── price_feed_contract.py
│   └── market_overview_contract.py
├── tests/
│   └── test_coingecko.py
├── setup.py
└── README.md
```

---

## API reference

### CoinGeckoClient

| Method | What it does |
|--------|-------------|
| `get_simple_price(ids, vs_currencies)` | Spot price for one or more coins |
| `get_coin_data(coin_id)` | Full coin detail — market data, description, links |
| `get_coin_market_chart(coin_id, days)` | Historical price series for charts |
| `get_top_coins(per_page)` | Top N by market cap |
| `get_trending()` | Trending on CoinGecko right now |
| `get_global_data()` | Total market cap, BTC dominance, volume |
| `get_prices_batch(coin_ids)` | Simplified multi-price lookup |

### CoinGeckoPriceFeed

| Method | What it does |
|--------|-------------|
| `get_price(coin_id, vs_currency)` | Single price |
| `get_prices(coin_ids, vs_currency)` | Multi-coin |
| `get_portfolio_value(holdings, vs_currency)` | Value a wallet |
| `get_price_with_market_context(coin_id)` | Enriched snapshot for LLM prompts |

---

## Adding other APIs

The base class makes it easy to wrap other REST APIs:

```python
from genlayer_integrations.base import BaseIntegration

class OpenWeatherMap(BaseIntegration):
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def get_weather(self, city: str):
        return self._request("/weather", {
            "q": city, "appid": self._api_key,
        })
```

---

## Tests

```bash
pip install -e .
python -m pytest tests/ -v
```

All tests use mocked HTTP — no network needed.

---

## License

MIT
