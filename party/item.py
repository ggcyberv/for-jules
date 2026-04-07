from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum, auto

class EquipSlot(Enum):
    WEAPON = auto()
    ARMOR = auto()
    HELM = auto()
    GLOVES = auto()
    BOOTS = auto()
    AMULET = auto()
    RING = auto()
    SHIELD = auto()

class Rarity(Enum):
    COMMON = ("Common", (255, 255, 255), 0, 1.0, 1)
    UNCOMMON = ("Uncommon", (30, 255, 0), 1, 1.2, 5)
    RARE = ("Rare", (0, 112, 221), 2, 1.5, 10)
    EPIC = ("Epic", (163, 53, 238), 3, 2.0, 15)
    LEGENDARY = ("Legendary", (255, 128, 0), 4, 2.5, 20)
    MYTHIC = ("Mythic", (255, 0, 0), 5, 3.0, 30)

    def __init__(self, label, color, affix_count, multiplier, min_level):
        self.label = label
        self.color = color
        self.affix_count = affix_count
        self.multiplier = multiplier
        self.min_level = min_level

@dataclass
class Affix:
    name: str
    stat: str # e.g. "STR", "hp", "crit_chance"
    value: float
    is_percent: bool = False
    is_prefix: bool = True # Prefix = base stats, Suffix = derived stats

@dataclass
class Item:
    item_id: str
    name: str
    description: str
    slot: EquipSlot
    rarity: Rarity = Rarity.COMMON
    item_level: int = 1
    value: int = 10
    weight: float = 1.0
    affixes: List[Affix] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        prefix = ""
        suffix = ""
        prefixes = [a for a in self.affixes if a.is_prefix]
        suffixes = [a for a in self.affixes if not a.is_prefix]
        if prefixes:
            prefix = prefixes[0].name + " "
        if suffixes:
            suffix = " " + suffixes[0].name
        return f"{prefix}{self.name}{suffix}"

@dataclass
class Weapon(Item):
    base_dmg_min: int = 0
    base_dmg_max: int = 0
    scaling: Dict[str, float] = field(default_factory=dict)
    is_two_handed: bool = False
    properties: Dict[str, float] = field(default_factory=dict) # e.g. {"ranged": 1.0, "reach": 1.0, "armor_pen": 0.1}

@dataclass
class Armor(Item):
    base_armor: int = 0
    speed_penalty: int = 0
    dodge_penalty: float = 0.0
    bonus_effects: Dict[str, float] = field(default_factory=dict)

@dataclass
class Shield(Armor):
    block_chance: float = 0.0

@dataclass
class Equipment:
    main_hand: Optional[Weapon] = None
    body: Optional[Armor] = None
    helm: Optional[Item] = None
    gloves: Optional[Item] = None
    boots: Optional[Item] = None
    amulet: Optional[Item] = None
    ring1: Optional[Item] = None
    ring2: Optional[Item] = None
    shield: Optional[Shield] = None
