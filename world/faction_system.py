from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

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
        self.relations: Dict[Tuple[str, str], int] = {} # (f1, f2) -> relation score

    def register_faction(self, faction: Faction):
        self.factions[faction.faction_id] = faction
        self.reputations[faction.faction_id] = faction.starting_reputation

        # Initialize relations with other factions
        for other_id in self.factions:
            if other_id != faction.faction_id:
                self.relations[(faction.faction_id, other_id)] = 0
                self.relations[(other_id, faction.faction_id)] = 0

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

    def adjust_faction_relation(self, faction_a: str, faction_b: str, amount: int):
        pair = tuple(sorted((faction_a, faction_b)))
        if pair not in self.relations:
            self.relations[pair] = 0
        self.relations[pair] = max(-100, min(100, self.relations[pair] + amount))

    def get_faction_relation(self, faction_a: str, faction_b: str) -> int:
        pair = tuple(sorted((faction_a, faction_b)))
        return self.relations.get(pair, 0)

@dataclass
class NPCParty:
    party_id: str
    faction_id: str
    name: str
    q: int
    r: int
    members: List[Any] # Characters
    behavior: str = "patrol" # patrol, chase, idle
    patrol_origin: Tuple[int, int] = (0, 0)

    def update(self, world, target_pos=None):
        from world.hex_grid import HexGrid
        if self.behavior == "chase" and target_pos:
            # Simple chase logic
            neighbors = world.get_neighbors(self.q, self.r)
            best_n = min(neighbors, key=lambda n: HexGrid.distance(n[0], n[1], target_pos[0], target_pos[1]))
            self.q, self.r = best_n
        elif self.behavior == "patrol":
            # Simple random patrol near origin
            neighbors = world.get_neighbors(self.q, self.r)
            valid_n = [n for n in neighbors if HexGrid.distance(n[0], n[1], self.patrol_origin[0], self.patrol_origin[1]) < 10]
            if valid_n:
                import random
                self.q, self.r = random.choice(valid_n)
