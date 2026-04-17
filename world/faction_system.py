from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

@dataclass
class Faction:
    faction_id: str
    name: str
    description: str
    starting_reputation: int = 0
    is_hostile: bool = False
    strategic_goals: List[str] = field(default_factory=list) # "Expansionist", "Mercantile", "Defensive"
    resources: Dict[str, int] = field(default_factory=lambda: {"gold": 1000, "influence": 10})
    capital_pos: Tuple[int, int] = (0, 0)

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

    def tick(self, world, turn) -> List['NPCParty']:
        from combat.combat_simulator import CombatSimulator
        import random
        new_parties = []
        # Faction-level AI: Expansion and Recruitment
        for faction_id, faction in self.factions.items():
            if faction_id == "citizens": continue # Player-allied usually

            # Resource income based on owned POIs would be better, but simplified for now
            faction.resources["gold"] += 50
            faction.resources["influence"] += 2

            # Expansion logic
            if "Expansionist" in faction.strategic_goals:
                if faction.resources["influence"] > 20:
                    faction.resources["influence"] -= 15
                    # Spawn Warband
                    new_id = f"{faction_id}_warband_{turn}_{random.randint(0, 999)}"
                    spawn_q, spawn_r = getattr(faction, "capital_pos", (0, 0))
                    npc = NPCParty(new_id, faction_id, f"{faction.name} Warband", spawn_q, spawn_r,
                                 [CombatSimulator.load_enemy("orc"), CombatSimulator.load_enemy("orc")],
                                 behavior="scout", patrol_origin=(spawn_q, spawn_r))
                    new_parties.append(npc)
                elif faction.resources["influence"] > 10:
                    faction.resources["influence"] -= 8
                    # Spawn Scout
                    new_id = f"{faction_id}_scout_{turn}_{random.randint(0, 999)}"
                    spawn_q, spawn_r = getattr(faction, "capital_pos", (0, 0))
                    npc = NPCParty(new_id, faction_id, f"{faction.name} Scout", spawn_q, spawn_r,
                                 [CombatSimulator.load_enemy("bandit")],
                                 behavior="scout", patrol_origin=(spawn_q, spawn_r))
                    new_parties.append(npc)

            if "Mercantile" in faction.strategic_goals and faction.resources["gold"] > 500:
                faction.resources["gold"] -= 300
                # Spawn Caravan
                new_id = f"{faction_id}_caravan_{turn}_{random.randint(0, 999)}"
                spawn_q, spawn_r = getattr(faction, "capital_pos", (0, 0))
                npc = NPCParty(new_id, faction_id, f"{faction.name} Caravan", spawn_q, spawn_r,
                             [CombatSimulator.load_enemy("bandit")],
                             behavior="trade", patrol_origin=(spawn_q, spawn_r))
                new_parties.append(npc)

        return new_parties

@dataclass
class NPCParty:
    party_id: str
    faction_id: str
    name: str
    q: int
    r: int
    members: List[Any] # Characters
    behavior: str = "patrol" # patrol, chase, idle, scout, trade
    patrol_origin: Tuple[int, int] = (0, 0)
    cargo: Dict[str, int] = field(default_factory=dict)

    def update(self, world, target_pos=None):
        from world.hex_grid import HexGrid
        import random

        # Claim territory
        tile = world.get_tile(self.q, self.r)
        if tile:
            tile.faction_influence = self.faction_id

        if self.behavior == "chase" and target_pos:
            neighbors = world.get_neighbors(self.q, self.r)
            best_n = min(neighbors, key=lambda n: HexGrid.distance(n[0], n[1], target_pos[0], target_pos[1]))
            self.q, self.r = best_n
        elif self.behavior == "patrol":
            neighbors = world.get_neighbors(self.q, self.r)
            valid_n = [n for n in neighbors if HexGrid.distance(n[0], n[1], self.patrol_origin[0], self.patrol_origin[1]) < 10]
            if valid_n:
                self.q, self.r = random.choice(valid_n)
        elif self.behavior == "scout":
            # Move towards nearest unowned tile or random neighbor
            neighbors = world.get_neighbors(self.q, self.r)
            unowned = [n for n in neighbors if (t := world.get_tile(n[0], n[1])) and t.faction_influence != self.faction_id]
            if unowned:
                self.q, self.r = random.choice(unowned)
            else:
                self.q, self.r = random.choice(neighbors)
        elif self.behavior == "trade":
            # Find nearest town and move towards it
            from engine.game_state import GameState
            state = GameState()
            towns = [l for l in state.locations.values() if l.location_type == "town"]
            if towns:
                nearest_town = min(towns, key=lambda t: HexGrid.distance(self.q, self.r, t.q, t.r))
                if HexGrid.distance(self.q, self.r, nearest_town.q, nearest_town.r) > 0:
                    neighbors = world.get_neighbors(self.q, self.r)
                    best_n = min(neighbors, key=lambda n: HexGrid.distance(n[0], n[1], nearest_town.q, nearest_town.r))
                    self.q, self.r = best_n
                else:
                    # At town: simulated trade
                    if hasattr(nearest_town, "commodities"):
                        # Just a placeholder for actual commodity exchange
                        pass
                    # Pick a new destination or wander
                    neighbors = world.get_neighbors(self.q, self.r)
                    self.q, self.r = random.choice(neighbors)
