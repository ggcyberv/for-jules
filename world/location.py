from dataclasses import dataclass, field
from typing import List, Dict, Optional
from party.character import Character

@dataclass
class TownNode:
    node_id: str
    name: str
    description: str
    service_type: str  # "market", "tavern", "healer", "recruit", "guild"

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
    # Node-based services
    nodes: List[TownNode] = field(default_factory=list)
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
    respawn_turn: int = 0
    loot_table: str = "default_dungeon"

@dataclass
class Watchtower(Location):
    location_type: str = "watchtower"
    vision_radius: int = 3
