from dataclasses import dataclass, field
from typing import List, Dict, Optional

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
    services: List[str] = field(default_factory=lambda: ["market", "tavern", "healer"])
    faction_id: Optional[str] = None
    inventory: List[str] = field(default_factory=list)

@dataclass
class Dungeon(Location):
    location_type: str = "dungeon"
    danger_level: float = 0.5
    is_cleared: bool = False
    loot_table: str = "default_dungeon"
