from typing import Dict

# Race Modifiers
RACE_MODS = {
    "Human": {"STR": 1, "AGI": 1, "CON": 1, "PER": 1, "INT": 1, "CHA": 1, "hp_bonus": 0.05, "mana_bonus": 0.05, "phys_res": 0.0, "mag_res": 0.0},
    "Elf": {"STR": 0, "AGI": 2, "CON": -1, "PER": 2, "INT": 1, "CHA": 0, "hp_bonus": -0.05, "mana_bonus": 0.15, "phys_res": 0.0, "mag_res": 0.05},
    "Dwarf": {"STR": 2, "AGI": 0, "CON": 2, "PER": 0, "INT": 0, "CHA": -1, "hp_bonus": 0.15, "mana_bonus": -0.05, "phys_res": 0.10, "mag_res": 0.05},
    "Orc": {"STR": 3, "AGI": 0, "CON": 2, "PER": -1, "INT": -2, "CHA": 0, "hp_bonus": 0.10, "mana_bonus": -0.10, "phys_res": 0.05, "mag_res": -0.05},
    "Halfling": {"STR": -1, "AGI": 3, "CON": 0, "PER": 1, "INT": 0, "CHA": 1, "hp_bonus": -0.05, "mana_bonus": 0.0, "phys_res": 0.0, "mag_res": 0.0},
    "Gnome": {"STR": -2, "AGI": 1, "CON": 0, "PER": 1, "INT": 3, "CHA": 1, "hp_bonus": -0.10, "mana_bonus": 0.20, "phys_res": -0.05, "mag_res": 0.10},
    "Dragonborn": {"STR": 2, "AGI": 0, "CON": 1, "PER": 0, "INT": 0, "CHA": 1, "hp_bonus": 0.10, "mana_bonus": 0.0, "phys_res": 0.05, "mag_res": 0.0},
    "Tiefling": {"STR": 0, "AGI": 1, "CON": 0, "PER": 1, "INT": 2, "CHA": 2, "hp_bonus": 0.0, "mana_bonus": 0.10, "phys_res": 0.0, "mag_res": 0.10}
}

# Age Modifiers
AGE_MODS = {
    "Young": {"STR": -1, "AGI": 2, "CON": 1, "PER": -1, "INT": -1, "CHA": 0, "xp_bonus": 0.05},
    "Adult": {"STR": 0, "AGI": 0, "CON": 0, "PER": 0, "INT": 0, "CHA": 1, "xp_bonus": 0.0},
    "Middle": {"STR": -1, "AGI": -1, "CON": -1, "PER": 1, "INT": 2, "CHA": 1},
    "Old": {"STR": -2, "AGI": -2, "CON": -2, "PER": 2, "INT": 3, "CHA": 2, "hp_mod": -0.10},
    "Venerable": {"STR": -3, "AGI": -3, "CON": -3, "PER": 3, "INT": 4, "CHA": 3, "hp_mod": -0.20}
}

# Size Modifiers
SIZE_MODS = {
    "Tiny": {"STR": -3, "CON": -2, "AGI": 4, "dodge_cap_mod": 0.15, "hp_mod": -0.20, "armor_mod": -0.15},
    "Small": {"STR": -1, "CON": -1, "AGI": 2, "dodge_cap_mod": 0.10, "hp_mod": -0.10, "armor_mod": -0.05},
    "Medium": {"STR": 0, "CON": 0, "AGI": 0, "dodge_cap_mod": 0.0, "hp_mod": 0.0, "armor_mod": 0.0},
    "Large": {"STR": 2, "CON": 2, "AGI": -2, "dodge_cap_mod": -0.05, "hp_mod": 0.15, "armor_mod": 0.10},
    "Huge": {"STR": 4, "CON": 3, "AGI": -4, "dodge_cap_mod": -0.10, "hp_mod": 0.30, "armor_mod": 0.20}
}

# Backstory Modifiers
BACKSTORY_MODS = {
    "Noble": {"CHA": 2, "INT": 1},
    "Outlander": {"STR": 2, "CON": 1},
    "Sage": {"INT": 3, "PER": 1},
    "Criminal": {"AGI": 3, "PER": 1},
    "Acolyte": {"CHA": 2, "CON": 2},
    "Soldier": {"STR": 2, "CON": 2},
    "Hermit": {"PER": 2, "INT": 2},
    "Merchant": {"CHA": 2, "AGI": 1}
}

# Weapon Types
WEAPON_TYPES = {
    "Dagger": {"base_dmg": (4, 8), "str_scale": 0.5, "agi_scale": 0.5, "crit_bonus": 5},
    "Sword": {"base_dmg": (8, 12), "str_scale": 0.8, "agi_scale": 0.2},
    "Axe": {"base_dmg": (12, 16), "str_scale": 1.0, "crit_dmg_bonus": 0.10},
    "Mace": {"base_dmg": (10, 14), "str_scale": 0.9, "armor_pen": 0.05},
    "Spear": {"base_dmg": (7, 11), "str_scale": 0.6, "agi_scale": 0.4, "dodge_bonus": 5},
    "Staff": {"base_dmg": (5, 9), "int_scale": 1.0, "mag_atk_bonus": 0.10},
    "Bow": {"base_dmg": (6, 10), "agi_scale": 1.0, "crit_bonus": 5}
}

# Armor Types
ARMOR_TYPES = {
    "Cloth": {"armor_range": (5, 15), "dodge_pen": 0.0, "speed_pen": 0.0, "mana_regen_bonus": 0.10},
    "Leather": {"armor_range": (15, 30), "dodge_pen": 0.05, "speed_pen": 0.02, "dodge_bonus": 0.05},
    "Chain": {"armor_range": (30, 50), "dodge_pen": 0.15, "speed_pen": 0.08, "phys_res_bonus": 0.05},
    "Plate": {"armor_range": (50, 80), "dodge_pen": 0.30, "speed_pen": 0.15, "armor_bonus": 0.10, "mag_res_penalty": 0.10}
}
