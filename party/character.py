from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import math
import random
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

    # Simulation fields
    needs: Dict[str, float] = field(default_factory=lambda: {"hunger": 0.0, "thirst": 0.0, "sleep": 0.0, "social": 0.0})
    personality_traits: List[str] = field(default_factory=list)
    goals: Dict[str, float] = field(default_factory=lambda: {"wealth": 0.5, "power": 0.2, "safety": 0.8})
    current_activity: Optional[Dict[str, Any]] = None
    last_social_tick: int = 0

    def set_loot(self, gold: int):
        self.loot_gold = gold
        return self

    @property
    def natural_str(self) -> int:
        if self.race not in RACE_MODS: return self.base_str
        return self.base_str + RACE_MODS[self.race]["STR"] + AGE_MODS[self.age_category]["STR"] + \
               SIZE_MODS[self.size]["STR"] + BACKSTORY_MODS[self.backstory_name]["STR"]

    @property
    def str(self) -> int:
        bonus = self.get_gear_bonus("STR")
        # Cap: Gear cannot increase base stat by more than 50%
        bonus = min(bonus, self.natural_str * 0.5)
        return int(self.natural_str + bonus)

    @property
    def natural_agi(self) -> int:
        if self.race not in RACE_MODS: return self.base_agi
        return self.base_agi + RACE_MODS[self.race]["AGI"] + AGE_MODS[self.age_category]["AGI"] + \
               SIZE_MODS[self.size]["AGI"] + BACKSTORY_MODS[self.backstory_name]["AGI"]

    @property
    def agi(self) -> int:
        bonus = self.get_gear_bonus("AGI")
        bonus = min(bonus, self.natural_agi * 0.5)
        return int(self.natural_agi + bonus)

    @property
    def natural_con(self) -> int:
        if self.race not in RACE_MODS: return self.base_con
        return self.base_con + RACE_MODS[self.race]["CON"] + AGE_MODS[self.age_category]["CON"] + \
               SIZE_MODS[self.size]["CON"] + BACKSTORY_MODS[self.backstory_name]["CON"]

    @property
    def con(self) -> int:
        bonus = self.get_gear_bonus("CON")
        bonus = min(bonus, self.natural_con * 0.5)
        return int(self.natural_con + bonus)

    @property
    def natural_per(self) -> int:
        if self.race not in RACE_MODS: return self.base_per
        return self.base_per + RACE_MODS[self.race]["PER"] + AGE_MODS[self.age_category]["PER"] + \
               BACKSTORY_MODS[self.backstory_name]["PER"]

    @property
    def per(self) -> int:
        bonus = self.get_gear_bonus("PER")
        bonus = min(bonus, self.natural_per * 0.5)
        return int(self.natural_per + bonus)

    @property
    def natural_int(self) -> int:
        if self.race not in RACE_MODS: return self.base_int
        return self.base_int + RACE_MODS[self.race]["INT"] + AGE_MODS[self.age_category]["INT"] + \
               BACKSTORY_MODS[self.backstory_name]["INT"]

    @property
    def int(self) -> int:
        bonus = self.get_gear_bonus("INT")
        bonus = min(bonus, self.natural_int * 0.5)
        return int(self.natural_int + bonus)

    @property
    def natural_cha(self) -> int:
        if self.race not in RACE_MODS: return self.base_cha
        return self.base_cha + RACE_MODS[self.race]["CHA"] + AGE_MODS[self.age_category]["CHA"] + \
               BACKSTORY_MODS[self.backstory_name]["CHA"]

    @property
    def cha(self) -> int:
        bonus = self.get_gear_bonus("CHA")
        bonus = min(bonus, self.natural_cha * 0.5)
        return int(self.natural_cha + bonus)

    @property
    def max_hp(self) -> int:
        base_hp = (self.con * 12) + (self.level * 8)
        size_mod = SIZE_MODS[self.size].get("hp_mod", 0)
        age_mod = AGE_MODS[self.age_category].get("hp_mod", 0)
        race_bonus = RACE_MODS[self.race].get("hp_bonus", 0) if self.race in RACE_MODS else 0
        gear_bonus = self.get_gear_bonus("hp")
        return int(base_hp * (1.0 + size_mod + age_mod + race_bonus) + gear_bonus)

    @property
    def max_mana(self) -> int:
        base_mana = (self.int * 10) + (self.level * 5) + (self.cha * 2)
        race_bonus = RACE_MODS[self.race].get("mana_bonus", 0) if self.race in RACE_MODS else 0
        gear_bonus = self.get_gear_bonus("mana")
        return int(base_mana * (1.0 + race_bonus) + gear_bonus)

    @property
    def speed(self) -> int:
        base_speed = 5 + (self.agi * 1.5) + (self.level * 0.5)
        gear_bonus = self.get_gear_bonus("speed")
        return int(base_speed + gear_bonus)

    @property
    def action_speed(self) -> float:
        return self.speed + (self.per * 0.5) + (self.level * 0.3)

    @property
    def phys_atk(self) -> float:
        base = (self.str * 3) + (self.level * 1.5)
        weapon_dmg = 0
        if self.equipment.main_hand:
            # Add base damage (scaled)
            weapon_dmg = random.randint(self.equipment.main_hand.base_dmg_min, self.equipment.main_hand.base_dmg_max)
            # Add scaling from base stats
            for stat, scale in self.equipment.main_hand.scaling.items():
                # Important: Use the character's active stat (with gear)
                weapon_dmg += getattr(self, stat.lower()) * scale

        flat_bonuses = self.get_gear_bonus("phys_atk")
        return base + weapon_dmg + flat_bonuses

    @property
    def mag_atk(self) -> float:
        base = (self.int * 4) + (self.per * 1) + (self.level * 1.2)
        flat_bonuses = self.get_gear_bonus("mag_atk")

        gear_mult = 1.0
        if self.equipment.main_hand and "mag_atk_bonus" in self.equipment.main_hand.properties:
            gear_mult += self.equipment.main_hand.properties["mag_atk_bonus"]

        return (base + flat_bonuses) * gear_mult

    @property
    def armor_val(self) -> float:
        size_mod = SIZE_MODS[self.size].get("armor_mod", 0)
        base_armor = (self.con * 1.5) + (self.str * 0.5)
        gear_armor = self.get_gear_bonus("armor")
        return (base_armor + gear_armor) * (1.0 + size_mod)

    @property
    def mag_res(self) -> float:
        base_res = (self.int * 1.2) + (self.cha * 1) + (self.level * 0.8)
        race_bonus = RACE_MODS[self.race].get("mag_res", 0)
        gear_bonus = self.get_gear_bonus("mag_res")
        return (base_res / 100.0) + race_bonus + gear_bonus

    @property
    def dodge_chance(self) -> float:
        base = 0.05 + (self.agi * 0.005) + (self.per * 0.0025) + (self.level * 0.002)
        gear_mod = self.get_gear_bonus("dodge")
        # respects cap (50% base, modified by size)
        cap = 0.5 + SIZE_MODS[self.size].get("dodge_cap_mod", 0)
        return max(0.0, min(cap, base + gear_mod))

    @property
    def crit_chance(self) -> float:
        base = (self.agi * 0.003) + (self.per * 0.004) + (self.level * 0.0015)
        gear_bonus = self.get_gear_bonus("crit_chance")
        if self.equipment.main_hand and "crit_chance" in self.equipment.main_hand.properties:
            gear_bonus += self.equipment.main_hand.properties["crit_chance"]
        return min(0.4, base + gear_bonus)

    @property
    def crit_damage(self) -> float:
        base = 1.5 + (self.int * 0.01) + (self.level * 0.005)
        gear_bonus = self.get_gear_bonus("crit_damage")
        if self.equipment.main_hand and "crit_damage" in self.equipment.main_hand.properties:
            gear_bonus += self.equipment.main_hand.properties["crit_damage"]
        return base + gear_bonus

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

    def get_gear_bonus(self, stat_name: str) -> float:
        total = 0.0
        slots = [
            self.equipment.main_hand, self.equipment.body, self.equipment.helm,
            self.equipment.gloves, self.equipment.boots, self.equipment.amulet,
            self.equipment.ring1, self.equipment.ring2, self.equipment.shield
        ]
        for item in slots:
            if not item: continue
            # Check fixed bonuses on Armor/Weapon
            if stat_name == "armor" and hasattr(item, "base_armor"):
                total += item.base_armor
            if stat_name == "dodge" and hasattr(item, "dodge_penalty"):
                total += item.dodge_penalty
            if stat_name == "speed" and hasattr(item, "speed_penalty"):
                total += item.speed_penalty
            if stat_name == "block_chance" and hasattr(item, "block_chance"):
                total += item.block_chance

            # Check Bonus Effects dict (for Armor)
            if hasattr(item, "bonus_effects") and stat_name in item.bonus_effects:
                total += item.bonus_effects[stat_name]

            # Check Affixes
            for affix in item.affixes:
                if affix.stat == stat_name:
                    total += affix.value
                # Handle special composite stat mappings
                if stat_name == "speed" and affix.stat == "speed_pct":
                    total += self.speed * affix.value

        return total

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
