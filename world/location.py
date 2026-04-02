from dataclasses import dataclass, field
from typing import List, Dict, Optional
from party.character import Character

@dataclass
class Location:
    poi_id: str
    name: str
    q: int
    r: int
    location_type: str  # "town", "dungeon", "resource_node"

@dataclass
class Town(Location):
    location_type: str = "town"
    services: List[str] = field(default_factory=lambda: ["market", "tavern", "healer", "recruit"])
    faction_id: Optional[str] = None
    inventory: List[str] = field(default_factory=list)
    healing_cost: int = 20
    recruits: List[Character] = field(default_factory=list)
    recruitment_cost: int = 100

@dataclass
class Dungeon(Location):
    location_type: str = "dungeon"
    danger_level: float = 0.5
    is_cleared: bool = False
    loot_table: str = "default_dungeon"
