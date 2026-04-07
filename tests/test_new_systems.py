import pytest
from world.hex_grid import HexGrid
from engine.game_state import GameState
from party.character import Character
from party.party_manager import Party
from combat.combat_simulator import CombatSimulator
from world.world_generator import WorldGenerator

def test_infinite_map_chunks():
    grid = HexGrid(chunk_size=10)
    gen = WorldGenerator(123, {"danger_level": 0.5})

    # Generate chunk 0,0
    gen.generate_chunk(grid, 0, 0)
    assert (0, 0) in grid.generated_chunks
    assert grid.get_tile(0, 0) is not None
    assert grid.get_tile(5, 5) is not None
    assert grid.get_tile(15, 15) is None

    # Generate distant chunk
    gen.generate_chunk(grid, 2, 2)
    assert (2, 2) in grid.generated_chunks
    assert grid.get_tile(25, 25) is not None

def test_character_effective_stats():
    from party.item import Weapon, Armor, EquipSlot, Rarity
    char = Character("Test", race="Human", backstory_name="Soldier", base_str=10)
    # STR 10 + Human 1 + Soldier 2 = 13. natural_phys_atk = 13*3 + 1*1.5 = 40.5

    char.equipment.main_hand = Weapon(
        item_id="sword", name="Sword", description="Blade", slot=EquipSlot.WEAPON,
        rarity=Rarity.COMMON, item_level=1, base_dmg_min=5, base_dmg_max=5
    )

    # Total Phys Atk = 40.5 + 5 = 45.5
    assert char.phys_atk == 45.5

def test_character_level_up():
    char = Character("Test", level=1, xp=0)
    char.gain_xp(1000) # New XP curve requires 1000 for lvl 2
    assert char.level == 2
    # Lvl 2 does not grant point (points at 4, 8, 12...)
    assert char.attribute_points == 0

def test_game_state_singleton():
    s1 = GameState()
    s2 = GameState()
    assert s1 is s2
