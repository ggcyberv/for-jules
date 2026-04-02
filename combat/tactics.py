from dataclasses import dataclass
from enum import Enum

class TacticType(Enum):
    BALANCED = "Balanced"
    AGGRESSIVE = "Aggressive"
    DEFENSIVE = "Defensive"

@dataclass
class TacticEffect:
    attack_mod: float = 1.0
    defense_mod: float = 1.0
    speed_mod: float = 1.0

TACTIC_EFFECTS = {
    TacticType.BALANCED: TacticEffect(),
    TacticType.AGGRESSIVE: TacticEffect(attack_mod=1.2, defense_mod=0.8),
    TacticType.DEFENSIVE: TacticEffect(attack_mod=0.8, defense_mod=1.2)
}
