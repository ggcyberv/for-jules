import random
import uuid
from typing import List, Dict, Any, Tuple
from party.item import Item, Weapon, Armor, Shield, Affix, Rarity, EquipSlot

# Constants based on doc
WEAPON_TYPES = {
    "Dagger": {"min_max": (6, 12), "scaling": {"STR": 0.5, "AGI": 0.5}, "properties": {"crit_chance": 0.05, "crit_damage": 0.10}},
    "Sword": {"min_max": (10, 18), "scaling": {"STR": 0.7, "AGI": 0.3}, "properties": {"accuracy": 0.05}},
    "Axe": {"min_max": (14, 22), "scaling": {"STR": 1.0}, "properties": {"armor_pen": 0.10}},
    "Mace": {"min_max": (12, 20), "scaling": {"STR": 0.9}, "properties": {"stun_chance": 0.10}},
    "Spear": {"min_max": (9, 15), "scaling": {"STR": 0.6, "AGI": 0.4}, "properties": {"dodge": 0.05, "reach": 1.0}},
    "Staff": {"min_max": (8, 14), "scaling": {"INT": 1.0}, "properties": {"mag_atk_bonus": 0.10, "mana_bonus": 0.05}},
    "Wand": {"min_max": (5, 9), "scaling": {"INT": 0.8, "PER": 0.2}, "properties": {"mana_regen": 0.10, "spell_crit": 0.05}},
    "Bow": {"min_max": (8, 14), "scaling": {"AGI": 1.0}, "properties": {"ranged": 1.0, "crit_damage": 0.10}},
    "Crossbow": {"min_max": (12, 18), "scaling": {"AGI": 1.0}, "properties": {"ranged": 1.0, "speed": -0.10, "armor_pen": 0.15}}
}

ARMOR_TYPES = {
    "Cloth": {"base_armor": (8, 15), "speed_pen": 0, "dodge_pen": 0.0, "bonus": {"mana_regen": 0.10}},
    "Leather": {"base_armor": (16, 30), "speed_pen": -2, "dodge_pen": -0.05, "bonus": {"dodge": 0.05}},
    "Chain": {"base_armor": (31, 50), "speed_pen": -8, "dodge_pen": -0.15, "bonus": {"phys_res": 0.05}},
    "Plate": {"base_armor": (51, 80), "speed_pen": -15, "dodge_pen": -0.30, "bonus": {"armor": 0.10, "mag_res": -0.10}}
}

PREFIX_POOL = [
    ("Vigorous", "CON", (2, 8)),
    ("Nimble", "AGI", (3, 12)),
    ("Brutal", "STR", (2, 10)),
    ("Wise", "INT", (3, 12)),
    ("Alert", "PER", (2, 8)),
    ("Charming", "CHA", (3, 10))
]

SUFFIX_POOL = [
    ("of the Bear", "hp", (15, 60)),
    ("of the Mage", "mana", (12, 50)),
    ("of Speed", "speed_pct", (0.03, 0.12)),
    ("of Evasion", "dodge", (0.05, 0.20)),
    ("of Protection", "armor", (10, 40)),
    ("of Resistance", "mag_res", (0.08, 0.30)),
    ("of Precision", "crit_chance", (0.03, 0.15)),
    ("of Devastation", "crit_damage", (0.10, 0.40))
]

UNIQUE_AFFIXES = [
    ("Life Leech", "life_leech", (0.05, 0.15)),
    ("Reflection", "reflect", (0.10, 0.20)),
    ("Haste", "haste", (0.10, 0.10)),
    ("Freezing", "freeze", (0.10, 0.10)),
    ("Shattering", "shattering", (0.20, 0.20))
]

class GearGenerator:
    @staticmethod
    def generate_item(item_level: int, rarity: Rarity = None) -> Item:
        if rarity is None:
            # Probability roll for rarity
            roll = random.random()
            if roll < 0.01: rarity = Rarity.MYTHIC
            elif roll < 0.05: rarity = Rarity.LEGENDARY
            elif roll < 0.15: rarity = Rarity.EPIC
            elif roll < 0.35: rarity = Rarity.RARE
            elif roll < 0.65: rarity = Rarity.UNCOMMON
            else: rarity = Rarity.COMMON

        # Force min level for rarity
        item_level = max(item_level, rarity.min_level)

        slot = random.choice(list(EquipSlot))

        if slot == EquipSlot.WEAPON:
            return GearGenerator._generate_weapon(item_level, rarity)
        elif slot == EquipSlot.ARMOR:
            return GearGenerator._generate_armor(item_level, rarity)
        elif slot == EquipSlot.SHIELD:
            return GearGenerator._generate_shield(item_level, rarity)
        else:
            return GearGenerator._generate_accessory(slot, item_level, rarity)

    @staticmethod
    def _generate_weapon(item_level: int, rarity: Rarity) -> Weapon:
        w_type_name = random.choice(list(WEAPON_TYPES.keys()))
        w_data = WEAPON_TYPES[w_type_name]

        # Scaling formulas
        scale_fact = 1 + (item_level - 1) * 0.015
        dmg_min = int(w_data["min_max"][0] * scale_fact)
        dmg_max = int(w_data["min_max"][1] * scale_fact)

        item = Weapon(
            item_id=str(uuid.uuid4()),
            name=w_type_name,
            description=f"A {rarity.label.lower()} {w_type_name.lower()}.",
            slot=EquipSlot.WEAPON,
            rarity=rarity,
            item_level=item_level,
            base_dmg_min=dmg_min,
            base_dmg_max=dmg_max,
            scaling=w_data["scaling"],
            properties=w_data["properties"].copy()
        )

        GearGenerator._apply_affixes(item, item_level, rarity)
        return item

    @staticmethod
    def _generate_armor(item_level: int, rarity: Rarity) -> Armor:
        a_type_name = random.choice(list(ARMOR_TYPES.keys()))
        a_data = ARMOR_TYPES[a_type_name]

        scale_fact = 1 + (item_level - 1) * 0.02
        base_arm = int(random.randint(a_data["base_armor"][0], a_data["base_armor"][1]) * scale_fact)

        item = Armor(
            item_id=str(uuid.uuid4()),
            name=f"{a_type_name} Chest",
            description=f"A {rarity.label.lower()} {a_type_name.lower()} chest piece.",
            slot=EquipSlot.ARMOR,
            rarity=rarity,
            item_level=item_level,
            base_armor=base_arm,
            speed_penalty=a_data["speed_pen"],
            dodge_penalty=a_data["dodge_pen"],
            bonus_effects=a_data["bonus"].copy()
        )

        GearGenerator._apply_affixes(item, item_level, rarity)
        return item

    @staticmethod
    def _generate_shield(item_level: int, rarity: Rarity) -> Shield:
        scale_fact = 1 + (item_level - 1) * 0.02
        base_arm = int(random.randint(15, 40) * scale_fact)
        block = 0.15 + (random.random() * 0.1)

        item = Shield(
            item_id=str(uuid.uuid4()),
            name="Shield",
            description="A sturdy shield.",
            slot=EquipSlot.SHIELD,
            rarity=rarity,
            item_level=item_level,
            base_armor=base_arm,
            block_chance=block,
            dodge_penalty=-0.10
        )
        GearGenerator._apply_affixes(item, item_level, rarity)
        return item

    @staticmethod
    def _generate_accessory(slot: EquipSlot, item_level: int, rarity: Rarity) -> Item:
        names = {
            EquipSlot.HELM: "Helm",
            EquipSlot.GLOVES: "Gloves",
            EquipSlot.BOOTS: "Boots",
            EquipSlot.AMULET: "Amulet",
            EquipSlot.RING: "Ring"
        }
        item = Item(
            item_id=str(uuid.uuid4()),
            name=names.get(slot, "Accessory"),
            description="A useful accessory.",
            slot=slot,
            rarity=rarity,
            item_level=item_level
        )
        GearGenerator._apply_affixes(item, item_level, rarity)
        return item

    @staticmethod
    def _apply_affixes(item: Item, item_level: int, rarity: Rarity):
        count = rarity.affix_count
        if count <= 0: return

        affix_scale = 1 + (item_level - 1) * 0.01

        available_prefixes = PREFIX_POOL.copy()
        available_suffixes = SUFFIX_POOL.copy()

        for i in range(count):
            # One mythic unique
            if rarity == Rarity.MYTHIC and i == 0:
                name, stat, val_range = random.choice(UNIQUE_AFFIXES)
                val = val_range[0] + random.random() * (val_range[1] - val_range[0])
                item.affixes.append(Affix(name, stat, val * rarity.multiplier, is_prefix=False))
                continue

            # Pick Prefix or Suffix
            if random.random() < 0.5 and available_prefixes:
                idx = random.randint(0, len(available_prefixes)-1)
                name, stat, val_range = available_prefixes.pop(idx)

                val = random.randint(val_range[0], val_range[1])
                item.affixes.append(Affix(name, stat, val * affix_scale * rarity.multiplier, is_prefix=True))
            elif available_suffixes:
                idx = random.randint(0, len(available_suffixes)-1)
                name, stat, val_range = available_suffixes.pop(idx)

                if isinstance(val_range[0], float):
                    val = val_range[0] + random.random() * (val_range[1] - val_range[0])
                else:
                    val = random.randint(val_range[0], val_range[1])

                item.affixes.append(Affix(name, stat, val * affix_scale * rarity.multiplier, is_prefix=False))
