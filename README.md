# GenLayer Price Oracle --- CoinGecko Integration

A Python library + Intelligent Contracts for fetching real-time cryptocurrency prices from CoinGecko on GenLayer. No oracles. No intermediaries. Just `gl.nondet.web.get()` and CoinGecko public API.

---

## What's inside

Two parts that work together:

**`src/genlayer_integrations/`** --- reusable Python library, useful for testing the CoinGecko API locally:

```python
from genlayer_integrations import CoinGeckoPriceFeed

feed = CoinGeckoPriceFeed()
btc = feed.get_price("bitcoin", "usd")
print(f"BTC: ${btc}")
```

**`examples/price_feed_contract.py`** --- ready-to-deploy Intelligent Contract that actually runs on-chain.

---

## Deploy to Testnet

### Prerequisites

- [GenLayer CLI](https://docs.genlayer.com/api-references/genlayer-cli) installed and `genlayer init` done
- An account with testnet funds (`genlayer account create` -> faucet at https://testnet-faucet.genlayer.foundation)
- Network set to Studionet (web access enabled):

```bash
genlayer network set studionet
```

### Deploy

```bash
genlayer deploy --contract examples/price_feed_contract.py

# Check initial state
genlayer call <CONTRACT> show_price
# -> No data

# Fetch Bitcoin price from CoinGecko
genlayer write <CONTRACT> fetch_price

# Read the stored price
genlayer call <CONTRACT> show_price
# -> bitcoin: 62623 usd
```

### Notes

- `genlayer deploy` uses `--contract` flag, not positional argument
- For `write` with simple string args, pass values directly: `--args bitcoin usd` (not JSON array)
- For `u256` / integer args, pass bare value: `--args 100` (not `[100]`)
- Web access (`gl.nondet.web.get()`) only works on Studionet. Asimov and Bradbury currently forbid external requests.
- The contract uses `gl.eq_principle.strict_eq()` so all validators agree on the result.

---

## Project layout

```
genlayer-price-oracle/
+-- src/genlayer_integrations/
|   +-- __init__.py
|   +-- base.py
|   +-- coingecko.py
|   +-- exceptions.py
+-- examples/
|   +-- price_feed_contract.py
+-- tests/
|   +-- test_coingecko.py
+-- setup.py
+-- README.md
```

---

## API reference

### CoinGeckoClient

| Method | What it does |
|--------|-------------|
| `get_simple_price(ids, vs_currencies)` | Spot price for one or more coins |
| `get_coin_data(coin_id)` | Full coin detail --- market data, description, links |
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

All tests use mocked HTTP --- no network needed.

---

## License

MIT
