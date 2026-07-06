# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class MarketOverviewContract(gl.Contract):
    summary: str

    def __init__(self):
        self.summary = "No data"

    @gl.public.view
    def get_summary(self) -> str:
        return self.summary

    @gl.public.write
    def fetch_market_overview(self) -> str:
        def fetch_market_data() -> str:
            ids = "bitcoin,ethereum,solana,ripple,cardano,polkadot,avalanche-2,chainlink"
            url = "https://api.coingecko.com/api/v3/simple/price?ids=" + ids + "&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true"
            r = gl.nondet.web.get(url)
            return r.body.decode("utf-8")

        try:
            raw = gl.eq_principle.strict_eq(fetch_market_data)
            d = json.loads(raw)

            if "status" in d and "error_code" in d["status"]:
                code = d["status"]["error_code"]
                msg = d["status"].get("error_message", "Unknown API error")
                self.summary = "API error (" + str(code) + "): " + msg
                return self.summary

            coins = []
            total_mcap = 0
            total_vol = 0
            for coin_id in d:
                info = d[coin_id]
                price = info.get("usd", 0)
                mcap = info.get("usd_market_cap", 0)
                vol = info.get("usd_24h_vol", 0)
                total_mcap += mcap
                total_vol += vol
                coins.append(coin_id + ": $" + str(price))

            self.summary = "MCap: $" + str(round(total_mcap)) + " | Vol: $" + str(round(total_vol)) + " | " + " | ".join(coins)
            return self.summary
        except Exception as e:
            self.summary = "Error: " + str(e)
            return self.summary