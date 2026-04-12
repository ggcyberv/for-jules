import pytest
from engine.models import Player, Hero, Character, Stats
from engine.manager import GameManager
from engine.map import GameMap

def test_hero_level_up():
    game_map = GameMap(10, 10)
    p1 = Player(1, "Player 1")
    char = Character("Valeria", "Fighter", Stats(16, 12, 14, 10, 10, 10), max_hp=30, current_hp=30, level=1, experience=0)
    h1 = Hero("Party 1", 1, position=(0, 0), party=[char])
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    # Gain 1500 XP (should reach level 2)
    # Level 1 needs 1000 XP to reach Level 2
    manager._award_xp(h1, 1500)

    assert char.level == 2
    assert char.experience == 500
    assert char.max_hp == 40

def test_hero_multi_level_up():
    game_map = GameMap(10, 10)
    p1 = Player(1, "Player 1")
    char = Character("Valeria", "Fighter", Stats(16, 12, 14, 10, 10, 10), max_hp=30, current_hp=30, level=1, experience=0)
    h1 = Hero("Party 1", 1, position=(0, 0), party=[char])
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    # Gain 4000 XP
    # L1->L2: 1000 XP (rem 3000)
    # L2->L3: 2000 XP (rem 1000)
    # L3->L4: 3000 XP -> wait my logic was different
    # Logic in manager.py: xp_required = char.level * 1000
    # L1: req 1000. Give 4000. L2, rem 3000.
    # L2: req 2000. Rem 3000. L3, rem 1000.
    # L3: req 3000. Rem 1000. Stay L3.
    # WAIT, I see what happened.
    # L1 -> L2: experience = 4000 - 1000 = 3000. level = 2.
    # Loop 2: experience = 3000. level = 2. xp_required = 2 * 1000 = 2000.
    # L2 -> L3: experience = 3000 - 2000 = 1000. level = 3.
    # Loop 3: experience = 1000. level = 3. xp_required = 3 * 1000 = 3000.
    # 1000 < 3000. Stop.
    # So it should be Level 3. Why did it get Level 5?
    # Ah! I didn't check manager.py carefully.

    manager._award_xp(h1, 4000)

    assert char.level == 3
