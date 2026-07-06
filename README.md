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
<img width="2506" height="1514" alt="5f0107a5-46d6-427f-a38b-19cec6584131" src="https://github.com/user-attachments/assets/24026b50-ebff-4845-ad94-55bb982fc112" />


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
<img width="2520" height="1386" alt="cc587752-ac91-4503-9cba-3d587ed19293" src="https://github.com/user-attachments/assets/40625132-e284-4700-ac22-adcee9b37947" />


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

- `show_price()` → returns the last stored price string
- `fetch_price(coin_id, vs_currency)` → fetches from CoinGecko and stores it

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

Global market snapshot (total market cap, volume, BTC dominance, active coins).

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

## Notes

- Studionet supports `gl.nondet.web.get()` for external HTTP requests. Asimov and Bradbury currently forbid it.
- `genlayer deploy --contract <file>`, not a positional arg.
- `--args bitcoin usd` passes two strings. For single numbers: `--args 100`.
- The `strict_eq` wrapper ensures all validators agree on the non-deterministic API result.
