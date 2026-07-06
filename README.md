# GenLayer Price Oracle -- CoinGecko

Intelligent Contracts that fetch live crypto prices from CoinGecko on GenLayer. No external oracles, just `gl.nondet.web.get()` calling the public CoinGecko API with `strict_eq` for validator consensus.

---

## Quick start

### Deploy to Studionet

```bash
# Switch to Studionet (web access required)
genlayer network set studionet

# Deploy
genlayer deploy --contract examples/price_feed_contract.py
```

### Fetch a price

```bash
# Default: bitcoin / usd
genlayer write <CONTRACT> fetch_price
genlayer call <CONTRACT> show_price
# -> bitcoin: 62623 usd

# Any supported coin
genlayer write <CONTRACT> fetch_price --args ethereum usd
genlayer call <CONTRACT> show_price
# -> ethereum: 1765 usd

genlayer write <CONTRACT> fetch_price --args solana usd
genlayer call <CONTRACT> show_price
# -> solana: 81 usd
```

### Coin/API ID

Use any CoinGecko coin slug. The slug is the last part of the coin page URL:

| Coin | CoinGecko URL | slug |
|------|--------------|------|
| Bitcoin | coingecko.com/en/coins/bitcoin | `bitcoin` |
| Ethereum | coingecko.com/en/coins/ethereum | `ethereum` |
| Solana | coingecko.com/en/coins/solana | `solana` |

Check the API directly to confirm:
```
https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
```

---

## Error handling

The contract retries up to 5 times on each `write` to handle API hiccups. Possible `show_price` outputs:

| Message | What it means |
|---------|---------------|
| `bitcoin: 62623 usd` | All good |
| `No data for "solana" after 5 retries` | API returned empty after 5 attempts -- try again |
| `API error (429): ...` | Rate limited -- wait a moment and retry |
| `Coin ID "xxx" not found in response` | Invalid slug or API returned unexpected data |

---

## Contract reference

### `price_feed_contract.py`

Simple single-price feed. Two methods:

- `show_price()` 鈫?returns the last stored price string
- `fetch_price(coin_id, vs_currency)` 鈫?fetches from CoinGecko and stores it

```python
@gl.public.write
def fetch_price(self, coin_id: str = "bitcoin", vs_currency: str = "usd") -> str:
    def fetch_from_coingecko() -> str:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=" + coin_id + "&vs_currencies=" + vs_currency
        # ... retries up to 5x ...
    raw = gl.eq_principle.strict_eq(fetch_from_coingecko)
    # ... parse & store ...
```

### `market_overview_contract.py`

Fetches top coins by market cap and computes a market snapshot in one call. Returns total market cap, 24h volume, and individual coin prices sorted by market cap (largest first).

```bash
genlayer deploy --contract examples/market_overview_contract.py
genlayer write <CONTRACT> fetch_market_overview
genlayer call <CONTRACT> get_summary
# -> MCap: $2228977441979 | Vol: $59506246744 | bitcoin: $61685 | ...
```

| Method | What it does |
|--------|-------------|
| `get_summary()` | Returns the last market snapshot string |
| `fetch_market_overview()` | Fetches top 10 coins with prices, market caps, volumes, then stores sorted summary |

The contract queries 10 major coins (bitcoin, ethereum, solana, ripple, cardano, polkadot, avalanche-2, chainlink, dogecoin, tron) in a single API call, then displays them ranked by market cap.

---

## Python library (for local testing)

The `src/genlayer_integrations/` package wraps the CoinGecko v3 API for local scripting:

```python
from genlayer_integrations import CoinGeckoPriceFeed

feed = CoinGeckoPriceFeed()
btc = feed.get_price("bitcoin", "usd")
```

---

## Project layout

```
genlayer-price-oracle/
|-- src/genlayer_integrations/
|   |-- __init__.py
|   |-- base.py
|   |-- coingecko.py
|   |-- exceptions.py
|-- examples/
|   |-- price_feed_contract.py
|   |-- market_overview_contract.py
|-- tests/
|   |-- test_coingecko.py
|-- setup.py
|-- README.md
```

---

## Notes

- Studionet supports `gl.nondet.web.get()` for external HTTP requests. Asimov and Bradbury currently forbid it.
- `genlayer deploy --contract <file>`, not a positional arg.
- `--args bitcoin usd` passes two strings. For single numbers: `--args 100`.
- The `strict_eq` wrapper ensures all validators agree on the non-deterministic API result.## License

MIT
