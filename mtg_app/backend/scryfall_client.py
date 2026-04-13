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
        # The /cards/autocomplete endpoint is English-focused.
        # For German support, we can use the /cards/search endpoint with the `lang` filter
        # or just rely on English autocomplete for simplicity if Scryfall's autocomplete is sufficient.
        # Actually, Scryfall's search API is better for multi-language support.
        # Let's try to support both. Scryfall's autocomplete doesn't support lang.
        # We can use /cards/search?q=name:/query/ or lang:de name:/query/

        # Simple English autocomplete first
        params = {"q": query}
        response = requests.get(f"{SCRYFALL_API_URL}/cards/autocomplete", params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []

    def search_cards(self, query: str, lang: Optional[str] = None) -> List[Dict]:
        self._rate_limit()
        # Example: q=name:"Grizzly Bears" lang:de
        q = f"name:\"{query}\"" if " " in query else query
        if lang:
            q += f" lang:{lang}"

        params = {"q": q, "include_multilingual": "true"}
        response = requests.get(f"{SCRYFALL_API_URL}/cards/search", params=params)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []

    def get_card_by_name(self, name: str) -> Optional[Dict]:
        self._rate_limit()
        params = {"exact": name}
        response = requests.get(f"{SCRYFALL_API_URL}/cards/named", params=params)
        if response.status_code == 200:
            return response.json()
        return None

    def get_card_details(self, oracle_id: str) -> Optional[Dict]:
        self._rate_limit()
        # Search for the newest regular printing
        # q=oracle_id:id -is:digital (order by released, dir desc)
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
        # Find the cheapest printing (non-foil, cardmarket price preferred as requested)
        params = {
            "q": f"oracle_id:{oracle_id}",
            "order": "usd", # Scryfall doesn't have "order by eur" directly in simple way but we can fetch all and compare
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
