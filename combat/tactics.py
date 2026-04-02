from dataclasses import dataclass
from enum import Enum

class TacticType(Enum):
    BALANCED = "Balanced"
    AGGRESSIVE = "Aggressive"
    DEFENSIVE = "Defensive"

class FormationType(Enum):
    NONE = "None"
    SHIELDWALL = "Shieldwall"
    SKIRMISH = "Skirmish"
    DOUBLE_LINE = "Double Line"
    CIRCLE = "Circle"

class AIPriority(Enum):
    NEAREST = "Nearest"
    WOUNDED = "Focus Wounded"
    HEALERS = "Focus Healers"
    CASTER = "Protect Caster"

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

FORMATION_EFFECTS = {
    FormationType.NONE: TacticEffect(),
    FormationType.SHIELDWALL: TacticEffect(defense_mod=1.3, speed_mod=0.7),
    FormationType.SKIRMISH: TacticEffect(attack_mod=1.1, speed_mod=1.2, defense_mod=0.9),
    FormationType.DOUBLE_LINE: TacticEffect(attack_mod=1.2, defense_mod=1.1),
    FormationType.CIRCLE: TacticEffect(defense_mod=1.5, attack_mod=0.7)
}
