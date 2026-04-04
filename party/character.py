from dataclasses import dataclass, field
from typing import List, Dict, Optional
from party.item import Equipment, Weapon, Armor

@dataclass
class Skill:
    name: str
    description: str
    level_required: int = 1

@dataclass
class Affliction:
    name: str
    stat_penalty: Dict[str, int]
    is_permanent: bool = False

@dataclass
class Character:
    name: str
    backstory: str = "A mysterious adventurer."
    level: int = 1
    xp: int = 0
    hp: int = 100
    max_hp: int = 100

    # Core Stats
    attack: int = 10
    defense: int = 10
    speed: int = 5

    # New Combat Attributes
    accuracy: int = 80 # Percentage
    critical_chance: int = 5 # Percentage
    luck: int = 0
    morale: int = 50
    max_morale: int = 100
    stamina: int = 100
    max_stamina: int = 100

    skills: List[Skill] = field(default_factory=list)
    relationships: Dict[str, int] = field(default_factory=dict)
    afflictions: List[Affliction] = field(default_factory=list)
    equipment: Equipment = field(default_factory=Equipment)
    attribute_points: int = 0
    combat_log: List[str] = field(default_factory=list)

    @property
    def fatigue_penalty(self) -> float:
        if self.stamina < 20: return 0.2 # 20% reduction
        if self.stamina < 50: return 0.1 # 10% reduction
        return 0.0

    @property
    def effective_attack(self) -> int:
        bonus = self.equipment.main_hand.attack_bonus if self.equipment.main_hand else 0
        penalty = sum(a.stat_penalty.get("attack", 0) for a in self.afflictions)
        base_eff = self.attack + bonus - penalty
        return max(1, int(base_eff * (1.0 - self.fatigue_penalty)))

    @property
    def effective_defense(self) -> int:
        bonus = self.equipment.body.defense_bonus if self.equipment.body else 0
        penalty = sum(a.stat_penalty.get("defense", 0) for a in self.afflictions)
        base_eff = self.defense + bonus - penalty
        return max(1, int(base_eff * (1.0 - self.fatigue_penalty)))

    @property
    def effective_speed(self) -> int:
        penalty = sum(a.stat_penalty.get("speed", 0) for a in self.afflictions)
        armor_penalty = self.equipment.body.speed_penalty if self.equipment.body else 0
        weapon_bonus = self.equipment.main_hand.speed_bonus if self.equipment.main_hand else 0
        return max(1, self.speed + weapon_bonus - penalty - armor_penalty)

    @property
    def effective_accuracy(self) -> int:
        bonus = self.equipment.main_hand.accuracy_bonus if hasattr(self.equipment.main_hand, 'accuracy_bonus') else 0
        return self.accuracy + bonus + self.luck

    def gain_xp(self, amount: int) -> bool:
        self.xp += amount
        if self.xp >= self.level * 100:
            self._level_up()
            return True
        return False

    def adjust_relationship(self, other_name: str, amount: int):
        self.relationships[other_name] = self.relationships.get(other_name, 0) + amount
        self.relationships[other_name] = max(-100, min(100, self.relationships[other_name]))

    def _level_up(self):
        self.xp -= self.level * 100
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.attribute_points += 2
        if self.level == 3:
            self.skills.append(Skill("Power Strike", "A heavy blow dealing massive damage."))
