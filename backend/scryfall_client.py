import requests
import time
from typing import List, Dict, Optional

SCRYFALL_API_URL = "https://api.scryfall.com"

class ScryfallClient:
    def __init__(self):
        self.last_request_time = 0
        self.request_delay = 0.1 # 100ms as per Scryfall API guidelines

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def autocomplete(self, query: str) -> List[str]:
        self._rate_limit()
        params = {"q": query}
        response = requests.get(f"{SCRYFALL_API_URL}/cards/autocomplete", params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []

    def search_cards(self, query: str, lang: Optional[str] = None, exact: bool = False) -> List[Dict]:
        self._rate_limit()
        if exact:
            q = f"!\"{query}\""
        else:
            q = f"name:\"{query}\"" if " " in query else query

        if lang:
            q += f" lang:{lang}"

        params = {"q": q, "include_multilingual": "true"}
        response = requests.get(f"{SCRYFALL_API_URL}/cards/search", params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []

    def get_card_details(self, oracle_id: str) -> Optional[Dict]:
        self._rate_limit()
        params = {
            "q": f"oracle_id:{oracle_id} -is:digital",
            "order": "released",
            "dir": "desc"
        }
        response = requests.get(f"{SCRYFALL_API_URL}/cards/search", params=params)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                return data[0]
        return None

    def get_cheapest_price(self, oracle_id: str) -> float:
        self._rate_limit()
        params = {
            "q": f"oracle_id:{oracle_id}",
        }
        response = requests.get(f"{SCRYFALL_API_URL}/cards/search", params=params)
        if response.status_code == 200:
            cards = response.json().get("data", [])
            prices = []
            for card in cards:
                eur = card.get("prices", {}).get("eur")
                if eur:
                    try:
                        prices.append(float(eur))
                    except ValueError:
                        continue
            if prices:
                return min(prices)
        return 0.0
