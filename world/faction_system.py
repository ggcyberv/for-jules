from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Faction:
    faction_id: str
    name: str
    description: str
    starting_reputation: int = 0
    is_hostile: bool = False

class FactionSystem:
    def __init__(self):
        self.factions: Dict[str, Faction] = {}
        self.reputations: Dict[str, int] = {} # faction_id -> rep score

    def register_faction(self, faction: Faction):
        self.factions[faction.faction_id] = faction
        self.reputations[faction.faction_id] = faction.starting_reputation

    def adjust_reputation(self, faction_id: str, amount: int):
        if faction_id in self.reputations:
            self.reputations[faction_id] += amount
            # Clamp reputation between -100 and 100
            self.reputations[faction_id] = max(-100, min(100, self.reputations[faction_id]))

    def get_reputation(self, faction_id: str) -> int:
        return self.reputations.get(faction_id, 0)

    def get_status(self, faction_id: str) -> str:
        rep = self.get_reputation(faction_id)
        if rep <= -50: return "Hostile"
        if rep < 0: return "Unfriendly"
        if rep < 50: return "Neutral"
        if rep < 90: return "Friendly"
        return "Allied"
