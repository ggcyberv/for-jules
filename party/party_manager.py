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
    max_ap: float = 10.0
    current_ap: float = 10.0
    forced_march: bool = False

    def add_member(self, character: Character):
        if len(self.members) < 6:
            self.members.append(character)
            return True
        return False

    def move_to(self, q: int, r: int, cost: float):
        self.forced_march = False
        if self.current_ap >= cost:
            # Consume stamina
            for m in self.members:
                m.stamina = max(0, m.stamina - int(cost * 5))
            self.q = q
            self.r = r
            self.current_ap -= cost
            return True
        elif len(self.members) > 0 and all(m.hp > 5 for m in self.members):
            # Forced march at the cost of HP
            self.q = q
            self.r = r
            self.current_ap = 0
            self.forced_march = True
            for m in self.members:
                m.hp -= 5
            return True
        return False

    def rest(self):
        self.current_ap = self.max_ap
        food_consumed = len(self.members) * 2

        if self.food >= food_consumed:
            self.food -= food_consumed
            for member in self.members:
                member.hp = min(member.max_hp, member.hp + 5)
                member.stamina = min(member.max_stamina, member.stamina + 20)
                member.morale = min(member.max_morale, member.morale + 2)
        else:
            self.food = 0
            # Starvation penalties
            for member in self.members:
                member.hp = max(1, member.hp - 10)
                member.morale = max(0, member.morale - 10)
                member.stamina = max(0, member.stamina - 10)
