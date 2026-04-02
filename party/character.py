from dataclasses import dataclass, field
from typing import List, Dict, Optional
from party.item import Equipment, Weapon, Armor

@dataclass
class Affliction:
    name: str
    stat_penalty: Dict[str, int]
    is_permanent: bool = False

@dataclass
class Character:
    name: str
    level: int = 1
    xp: int = 0
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 10
    speed: int = 5
    skills: List[str] = field(default_factory=list)
    relationships: Dict[str, int] = field(default_factory=dict)
    afflictions: List[Affliction] = field(default_factory=list)
    equipment: Equipment = field(default_factory=Equipment)
    attribute_points: int = 0

    @property
    def effective_attack(self) -> int:
        bonus = self.equipment.main_hand.attack_bonus if self.equipment.main_hand else 0
        penalty = sum(a.stat_penalty.get("attack", 0) for a in self.afflictions)
        return max(1, self.attack + bonus - penalty)

    @property
    def effective_defense(self) -> int:
        bonus = self.equipment.body.defense_bonus if self.equipment.body else 0
        penalty = sum(a.stat_penalty.get("defense", 0) for a in self.afflictions)
        return max(1, self.defense + bonus - penalty)

    @property
    def effective_speed(self) -> int:
        penalty = sum(a.stat_penalty.get("speed", 0) for a in self.afflictions)
        armor_penalty = self.equipment.body.speed_penalty if self.equipment.body else 0
        weapon_bonus = self.equipment.main_hand.speed_bonus if self.equipment.main_hand else 0
        return max(1, self.speed + weapon_bonus - penalty - armor_penalty)

    def gain_xp(self, amount: int):
        self.xp += amount
        if self.xp >= self.level * 100:
            self._level_up()

    def _level_up(self):
        self.xp -= self.level * 100
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.attribute_points += 2
