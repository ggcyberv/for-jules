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
        try:
            response = requests.get(f"{SCRYFALL_API_URL}/cards/autocomplete", params=params, timeout=5)
            if response.status_code == 200:
                return response.json().get("data", [])
        except requests.exceptions.RequestException:
            pass
        return []

    def search_cards(self, query: str, lang: Optional[str] = None, exact: bool = False) -> List[Dict]:
        self._rate_limit()
        if exact:
            q = f"!\"{query}\""
        else:
            # If query already contains search operators like set:, oracle_id:, etc.
            # we should not wrap it in name:""
            if ":" in query:
                q = query
            else:
                q = f"name:\"{query}\"" if " " in query else query

        if lang:
            q += f" lang:{lang}"

        params = {"q": q, "include_multilingual": "true"}
        all_data = []
        url = f"{SCRYFALL_API_URL}/cards/search"

        while url:
            try:
                response = requests.get(url, params=params, timeout=10)
                params = None # Only first call uses params
                if response.status_code == 200:
                    data = response.json()
                    all_data.extend(data.get("data", []))
                    if data.get("has_more"):
                        url = data.get("next_page")
                        self._rate_limit()
                    else:
                        url = None
                else:
                    url = None
            except requests.exceptions.RequestException:
                url = None
        return all_data

    def get_card_details(self, oracle_id: str) -> Optional[Dict]:
        self._rate_limit()
        # First try searching for newest printing
        params = {
            "q": f"oracle_id:{oracle_id} -is:digital",
            "order": "released",
            "dir": "desc"
        }
        try:
            response = requests.get(f"{SCRYFALL_API_URL}/cards/search", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    return data[0]

            # If no digital-filtered result, try search without it
            params["q"] = f"oracle_id:{oracle_id}"
            response = requests.get(f"{SCRYFALL_API_URL}/cards/search", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    return data[0]
        except requests.exceptions.RequestException:
            pass

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

    def get_collection_batch(self, identifiers: List[Dict]) -> List[Dict]:
        """Fetch multiple cards in one request. Up to 75 identifiers."""
        self._rate_limit()
        try:
            response = requests.post(f"{SCRYFALL_API_URL}/cards/collection", json={"identifiers": identifiers}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
        except requests.exceptions.RequestException:
            pass
        return []
