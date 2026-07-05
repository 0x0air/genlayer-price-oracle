# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class PriceFeedContract(gl.Contract):
    """Cryptocurrency price feed from CoinGecko."""

    last_price: str
    last_update: u256

    def __init__(self):
        self.last_price = "No data"
        self.last_update = u256(0)

    @gl.public.view
    def show_price(self) -> str:
        return self.last_price

    @gl.public.write
    def fetch_price(self, coin_id: str = "bitcoin", vs_currency: str = "usd") -> str:
        """Fetch live price from CoinGecko."""
        url = "https://api.coingecko.com/api/v3/simple/price?ids=" + coin_id + "&vs_currencies=" + vs_currency
        r = gl.nondet.web.get(url)
        if r.status_code != 200:
            return "HTTP Error: " + str(r.status_code)
        data = json.loads(r.body.decode("utf-8"))
        if coin_id not in data:
            return "Coin not found: " + coin_id
        price = data[coin_id][vs_currency]
        self.last_price = coin_id + ": " + str(price) + " " + vs_currency
        self.last_update = u256(__import__("time").time())
        return self.last_price
