# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class PriceFeedContract(gl.Contract):
    last_price: str

    def __init__(self):
        self.last_price = "No data"

    @gl.public.view
    def show_price(self) -> str:
        return self.last_price

    @gl.public.write
    def fetch_price(self) -> str:
        def fetch_from_coingecko() -> str:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            r = gl.nondet.web.get(url)
            return r.body.decode("utf-8")

        try:
            raw = gl.eq_principle.strict_eq(fetch_from_coingecko)
            data = json.loads(raw)
            price = data["bitcoin"]["usd"]
            self.last_price = "bitcoin: " + str(price) + " usd"
            return self.last_price
        except gl.UserError as e:
            return "Error: " + e.message
        except Exception as e:
            return "Error: " + str(e)
