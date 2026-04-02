from dataclasses import dataclass, field
from typing import List, Optional, Dict
import uuid

@dataclass(frozen=True)
class UnitType:
    name: str
    attack: int
    defense: int
    health: int
    damage_min: int
    damage_max: int
    speed: int
    cost: Dict[str, int]
    upkeep: int
    size: int

@dataclass
class Stack:
    unit_type: UnitType
    quantity: int
    stack_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Hero:
    name: str
    owner_id: int
    position: tuple = (0, 0)
    army: List[Stack] = field(default_factory=list)
    movement_points: int = 10
    max_movement_points: int = 10
    level: int = 1
    experience: int = 0
    skills: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)

@dataclass
class POI:
    poi_id: str
    poi_type: str  # 'town', 'mine', 'fort', etc.
    position: tuple
    control_value: int
    owner_id: Optional[int] = None
    garrison: List[Stack] = field(default_factory=list)
    income: Dict[str, int] = field(default_factory=dict)
    turns_held: int = 0
    recruitable_units: List[UnitType] = field(default_factory=list)

@dataclass
class Player:
    player_id: int
    name: str
    resources: Dict[str, int] = field(default_factory=lambda: {"gold": 1000, "wood": 0, "ore": 0, "gems": 0})
    heroes: List[Hero] = field(default_factory=list)
    winning_streak: int = 0
    owned_pois: List[str] = field(default_factory=list) # List of POI IDs
