# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class MarketOverviewContract(gl.Contract):
    """Global crypto market stats from CoinGecko."""

    summary: str

    def __init__(self):
        self.summary = "No data"

    @gl.public.view
    def get_summary(self) -> str:
        return self.summary

    @gl.public.write
    def fetch_market_overview(self) -> str:
        def fetch_global() -> str:
            r = gl.nondet.web.get("https://api.coingecko.com/api/v3/global")
            return r.body.decode("utf-8")

        try:
            raw = gl.eq_principle.strict_eq(fetch_global)
            data = json.loads(raw)
            mcap = str(data.get('total_market_cap', {}).get('usd', 'N/A'))
            volume = str(data.get('total_volume', {}).get('usd', 'N/A'))
            btc_dom = str(data.get('market_cap_percentage', {}).get('btc', 'N/A'))
            coins = str(data.get('active_cryptocurrencies', 'N/A'))
            self.summary = "Total MCap: " + mcap + " | Vol: " + volume + " | BTC: " + btc_dom + "% | Coins: " + coins
            return self.summary
        except Exception as e:
            return "Error: " + str(e)
