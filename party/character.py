from dataclasses import dataclass, field
from typing import List, Dict, Optional

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
    inventory: List[str] = field(default_factory=list)
    relationships: Dict[str, int] = field(default_factory=dict)
    afflictions: List[Affliction] = field(default_factory=list)

    @property
    def effective_attack(self) -> int:
        penalty = sum(a.stat_penalty.get("attack", 0) for a in self.afflictions)
        return max(1, self.attack - penalty)

    @property
    def effective_defense(self) -> int:
        penalty = sum(a.stat_penalty.get("defense", 0) for a in self.afflictions)
        return max(1, self.defense - penalty)

    def gain_xp(self, amount: int):
        self.xp += amount
        if self.xp >= self.level * 100:
            self._level_up()

    def _level_up(self):
        self.xp -= self.level * 100
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.attack += 2
        self.defense += 2
