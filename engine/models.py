from dataclasses import dataclass, field
from typing import List, Optional, Dict
import uuid

@dataclass
class Stats:
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

@dataclass
class Item:
    name: str
    item_type: str  # 'weapon', 'armor', 'consumable'
    modifiers: Dict[str, int] = field(default_factory=dict)
    description: str = ""

@dataclass
class Inventory:
    items: List[Item] = field(default_factory=list)
    capacity: int = 20

@dataclass
class Character:
    name: str
    char_class: str
    char_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stats: Stats = field(default_factory=Stats)
    max_hp: int = 10
    current_hp: int = 10
    level: int = 1
    experience: int = 0
    inventory: Inventory = field(default_factory=Inventory)
    equipment: Dict[str, Optional[Item]] = field(default_factory=lambda: {
        "weapon": None,
        "armor": None
    })
    skills: List[str] = field(default_factory=list)

    def get_modifier(self, stat_name: str) -> int:
        val = getattr(self.stats, stat_name)
        return (val - 10) // 2

    def __hash__(self):
        return hash(self.char_id)

    @property
    def ac(self) -> int:
        base_ac = 10 + self.get_modifier("dexterity")
        if self.equipment["armor"]:
            base_ac += self.equipment["armor"].modifiers.get("ac", 0)
        return base_ac

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
    party: List[Character] = field(default_factory=list)
    movement_points: int = 10
    max_movement_points: int = 10

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
