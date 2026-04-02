from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any
from party.character import Character

@dataclass
class Party:
    members: List[Character] = field(default_factory=list)
    inventory: List[Any] = field(default_factory=list)
    gold: int = 100
    food: int = 50
    q: int = 0
    r: int = 0
    max_ap: int = 10
    current_ap: int = 10

    def add_member(self, character: Character):
        if len(self.members) < 6:
            self.members.append(character)
            return True
        return False

    def move_to(self, q: int, r: int, cost: int):
        if self.current_ap >= cost:
            self.q = q
            self.r = r
            self.current_ap -= cost
            return True
        return False

    def rest(self):
        self.current_ap = self.max_ap
        food_consumed = len(self.members) * 2
        self.food = max(0, self.food - food_consumed)
        for member in self.members:
            member.hp = min(member.max_hp, member.hp + 5)
