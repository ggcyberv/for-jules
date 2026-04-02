from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Item:
    item_id: str
    name: str
    description: str
    value: int = 10
    weight: float = 1.0

@dataclass
class Weapon(Item):
    attack_bonus: int = 0
    speed_bonus: int = 0

@dataclass
class Armor(Item):
    defense_bonus: int = 0
    speed_penalty: int = 0

@dataclass
class Equipment:
    main_hand: Optional[Weapon] = None
    body: Optional[Armor] = None
    accessory: Optional[Item] = None
