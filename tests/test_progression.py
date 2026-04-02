import pytest
from engine.models import Player, Hero, Stack, UnitType
from engine.manager import GameManager
from engine.map import GameMap

def test_hero_level_up():
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    game_map = GameMap(10, 10)
    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(0,0), level=1, experience=0, max_movement_points=10)
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    # Gain 150 XP (should reach level 2)
    # Level 1 needs 100 XP to reach Level 2
    manager._award_xp(h1, 150)

    assert h1.level == 2
    assert h1.experience == 50 # 150 - 100
    assert h1.max_movement_points == 12

def test_hero_multi_level_up():
    game_map = GameMap(10, 10)
    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(0,0), level=1, experience=0, max_movement_points=10)

    manager = GameManager(game_map, [p1])

    # Gain 400 XP
    # L1->L2: 100 XP (rem 300)
    # L2->L3: 200 XP (rem 100)
    # L3->L4: 300 XP (not enough, rem 100)
    manager._award_xp(h1, 400)

    assert h1.level == 3
    assert h1.experience == 100
    assert h1.max_movement_points == 14
