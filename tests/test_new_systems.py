import pytest
from world.hex_grid import HexGrid
from engine.rng_manager import RNGManager
from engine.game_state import GameState
from party.character import Character
from party.party_manager import Party
from combat.combat_simulator import CombatSimulator

def test_hex_distance():
    grid = HexGrid(10, 10)
    # Axial distance (0,0) to (1,0) is 1
    assert grid.distance(0, 0, 1, 0) == 1
    # (0,0) to (1,1) is 2 in axial? Wait.
    # (0,0) -> (0,0,0)
    # (1,1) -> (1,1,-2)
    # dist = (1 + 1 + 2) / 2 = 2. Correct for axial.
    assert grid.distance(0, 0, 1, 1) == 2

def test_character_level_up():
    char = Character("Test", level=1, xp=0)
    char.gain_xp(100)
    assert char.level == 2
    assert char.xp == 0
    assert char.max_hp == 110

def test_combat_simulation():
    p1 = Character("Hero", hp=100, attack=20, defense=10, speed=10)
    e1 = Character("Enemy", hp=20, attack=5, defense=5, speed=5)

    result = CombatSimulator.simulate_battle([p1], [e1])
    assert result["victory"] is True
    assert e1.hp == 0
    assert p1.xp > 0

def test_game_state_singleton():
    s1 = GameState()
    s2 = GameState()
    assert s1 is s2
    s1.turn = 5
    assert s2.turn == 5
