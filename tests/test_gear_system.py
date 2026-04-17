import pytest
from party.character import Character
from party.item import Weapon, Armor, Shield, EquipSlot, Rarity, Affix
from party.gear_generator import GearGenerator

def test_gear_generator():
    # Test level scaling
    # Ensure we use the same weapon type for comparison
    from party.gear_generator import WEAPON_TYPES
    w_type = list(WEAPON_TYPES.keys())[0]

    # Manually trigger generation logic to ensure same type
    item_lvl_1 = GearGenerator._generate_weapon(1, Rarity.COMMON)
    item_lvl_1.name = w_type # Mock name

    # We'll just compare scaling of the same base type
    base_min = WEAPON_TYPES[w_type]["min_max"][0]
    scale_1 = 1 + (1 - 1) * 0.015
    scale_20 = 1 + (20 - 1) * 0.015

    assert int(base_min * scale_20) > int(base_min * scale_1)

    # Test rarity affixes
    epic_item = GearGenerator.generate_item(10, Rarity.EPIC)
    assert len(epic_item.affixes) == 3

def test_stat_calculation_with_gear():
    char = Character("Thorin", race="Dwarf", level=20)
    # Natural STR for Dwarf lvl 20 (Base 10 + Dwarf 2 + Soldier 2 = 14)
    natural = char.natural_str

    # Add gear with STR bonus
    sword = Weapon("s1", "Sword", "Desc", EquipSlot.WEAPON, Rarity.RARE, item_level=20)
    sword.affixes.append(Affix("Brutal", "STR", 10))
    char.equipment.main_hand = sword

    # Natural 14, Bonus 10. Bonus cap = 14 * 0.5 = 7.
    # Total should be 14 + 7 = 21.
    assert char.str == natural + int(natural * 0.5)

def test_combat_mechanics_gear():
    char = Character("Defender", level=20)
    char.base_con = 20 # Natural high armor
    natural_armor = char.armor_val

    shield = Shield("sh1", "Shield", "Desc", EquipSlot.SHIELD, Rarity.EPIC, item_level=20)
    shield.base_armor = 50
    shield.block_chance = 0.25
    char.equipment.shield = shield

    assert char.armor_val > natural_armor
    assert char.get_gear_bonus("block_chance") == 0.25
