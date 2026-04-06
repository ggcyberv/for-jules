from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math
from party.item import Equipment, Weapon, Armor
from engine.stats_config import RACE_MODS, AGE_MODS, SIZE_MODS, BACKSTORY_MODS, WEAPON_TYPES, ARMOR_TYPES

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
    backstory_name: str = "Soldier"
    backstory: str = "A mysterious adventurer."
    race: str = "Human"
    age_category: str = "Adult"
    size: str = "Medium"
    level: int = 1
    xp: int = 0

    # New Base Stats
    base_str: int = 10
    base_agi: int = 10
    base_con: int = 10
    base_per: int = 10
    base_int: int = 10
    base_cha: int = 10

    # Resource Current Values
    hp: int = 100
    mana: int = 50

    # NPC Basic Stats (fallback for Character model)
    npc_attack: int = 5
    npc_defense: int = 5
    npc_speed: int = 3

    # Status Stats
    morale: int = 50
    max_morale: int = 100
    stamina: int = 100
    max_stamina: int = 100
    luck: int = 0

    skills: List[Skill] = field(default_factory=list)

    # Tactical Preferences
    combat_tactic: str = "Balanced" # TacticType.BALANCED.value
    combat_priority: str = "Nearest" # AIPriority.NEAREST.value
    heal_threshold: int = 30 # Percentage

    relationships: Dict[str, int] = field(default_factory=dict)
    afflictions: List[Affliction] = field(default_factory=list)
    equipment: Equipment = field(default_factory=Equipment)
    attribute_points: int = 0
    combat_log: List[str] = field(default_factory=list)
    loot_gold: int = 0

    def set_loot(self, gold: int):
        self.loot_gold = gold
        return self

    @property
    def str(self) -> int:
        if self.race == "NPC": return self.npc_attack # Map NPC attack to str for legacy compatibility
        return self.base_str + RACE_MODS[self.race]["STR"] + AGE_MODS[self.age_category]["STR"] + \
               SIZE_MODS[self.size]["STR"] + BACKSTORY_MODS[self.backstory_name]["STR"]

    @property
    def agi(self) -> int:
        if self.race == "NPC": return self.npc_speed
        return self.base_agi + RACE_MODS[self.race]["AGI"] + AGE_MODS[self.age_category]["AGI"] + \
               SIZE_MODS[self.size]["AGI"] + BACKSTORY_MODS[self.backstory_name]["AGI"]

    @property
    def con(self) -> int:
        if self.race == "NPC": return 10
        return self.base_con + RACE_MODS[self.race]["CON"] + AGE_MODS[self.age_category]["CON"] + \
               SIZE_MODS[self.size]["CON"] + BACKSTORY_MODS[self.backstory_name]["CON"]

    @property
    def per(self) -> int:
        if self.race == "NPC": return 10
        return self.base_per + RACE_MODS[self.race]["PER"] + AGE_MODS[self.age_category]["PER"] + \
               BACKSTORY_MODS[self.backstory_name]["PER"]

    @property
    def int(self) -> int:
        if self.race == "NPC": return 10
        return self.base_int + RACE_MODS[self.race]["INT"] + AGE_MODS[self.age_category]["INT"] + \
               BACKSTORY_MODS[self.backstory_name]["INT"]

    @property
    def cha(self) -> int:
        if self.race == "NPC": return 10
        return self.base_cha + RACE_MODS[self.race]["CHA"] + AGE_MODS[self.age_category]["CHA"] + \
               BACKSTORY_MODS[self.backstory_name]["CHA"]

    @property
    def max_hp(self) -> int:
        if self.race == "NPC": return self.hp # NPCs use set hp
        base_hp = (self.con * 12) + (self.level * 8)
        size_mod = SIZE_MODS[self.size].get("hp_mod", 0)
        age_mod = AGE_MODS[self.age_category].get("hp_mod", 0)
        race_bonus = RACE_MODS[self.race].get("hp_bonus", 0)
        return int(base_hp * (1.0 + size_mod + age_mod + race_bonus))

    @property
    def max_mana(self) -> int:
        base_mana = (self.int * 10) + (self.level * 5) + (self.cha * 2)
        race_bonus = RACE_MODS[self.race].get("mana_bonus", 0)
        return int(base_mana * (1.0 + race_bonus))

    @property
    def speed(self) -> int:
        if self.race == "NPC": return self.npc_speed
        base_speed = 5 + (self.agi * 1.5) + (self.level * 0.5)
        # Size/Age speed mods not explicitly in doc but implies
        return int(base_speed)

    @property
    def action_speed(self) -> float:
        return self.speed + (self.per * 0.5) + (self.level * 0.3)

    @property
    def phys_atk(self) -> float:
        # Finesse check: if main hand is Dagger or Bow, add AGI
        finesse = 0
        if self.equipment.main_hand:
            # We'll use a simple name check or add a property to Weapon
            if "Dagger" in self.equipment.main_hand.name or "Bow" in self.equipment.main_hand.name:
                finesse = self.agi
        return (self.str * 3) + finesse + (self.level * 1.5)

    @property
    def mag_atk(self) -> float:
        bonus = 0
        if self.equipment.main_hand and "Staff" in self.equipment.main_hand.name:
            bonus = 10 # Focus_Item_Bonus example
        return (self.int * 4) + (self.per * 1) + (self.level * 1.2) + bonus

    @property
    def armor_val(self) -> float:
        gear_armor = self.equipment.body.defense_bonus if self.equipment.body else 0
        size_mod = SIZE_MODS[self.size].get("armor_mod", 0)
        base_armor = (self.con * 1.5) + (self.str * 0.5) + gear_armor
        return base_armor * (1.0 + size_mod)

    @property
    def mag_res(self) -> float:
        base_res = (self.int * 1.2) + (self.cha * 1) + (self.level * 0.8)
        race_bonus = RACE_MODS[self.race].get("mag_res", 0)
        # Gear resist?
        return (base_res / 100.0) + race_bonus

    @property
    def dodge_chance(self) -> float:
        size_penalty = 0 # SIZE_MODS doesn't explicitly have penalty but has cap mod
        base = 0.05 + (self.agi * 0.005) + (self.per * 0.0025) + (self.level * 0.002)
        # Gear penalty from Armor?
        gear_penalty = 0
        if self.equipment.body:
            # Look up in ARMOR_TYPES if we can identify it
            pass
        return min(0.5 + SIZE_MODS[self.size].get("dodge_cap_mod", 0), base - gear_penalty)

    @property
    def crit_chance(self) -> float:
        base = (self.agi * 0.003) + (self.per * 0.004) + (self.level * 0.0015)
        return min(0.4, base)

    @property
    def crit_damage(self) -> float:
        return 1.5 + (self.int * 0.01) + (self.level * 0.005)

    @property
    def fatigue_penalty(self) -> float:
        if self.stamina < 20: return 0.2
        if self.stamina < 50: return 0.1
        return 0.0

    def gain_xp(self, amount: int) -> bool:
        xp_mod = 1.0 + AGE_MODS[self.age_category].get("xp_bonus", 0)
        self.xp += int(amount * xp_mod)
        if self.xp >= self.xp_required:
            self._level_up()
            return True
        return False

    @property
    def xp_required(self) -> int:
        if self.level <= 20:
            return int(1000 * (1.1 ** (self.level - 1)))
        return int(1000 * (1.15 ** (self.level - 1)))

    def adjust_relationship(self, other_name: str, amount: int):
        self.relationships[other_name] = self.relationships.get(other_name, 0) + amount
        self.relationships[other_name] = max(-100, min(100, self.relationships[other_name]))

    def _level_up(self):
        self.xp -= self.xp_required
        self.level += 1
        self.hp = self.max_hp
        self.mana = self.max_mana

        # Base stats: +1 every 4 levels (choose which stat)
        if self.level % 4 == 0:
            self.attribute_points += 1

        if self.level == 3:
            self.skills.append(Skill("Power Strike", "A heavy blow dealing massive damage."))
