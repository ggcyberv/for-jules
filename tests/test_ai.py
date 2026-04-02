import pytest
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.map import GameMap
from engine.manager import GameManager
from engine.ai import BasicAI

def test_ai_moves_toward_poi():
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    game_map = GameMap(10, 10)

    # POI at (3, 3)
    poi = POI("mine1", "mine", (3, 3), 1)
    game_map.set_poi(poi)

    # AI Player at (0, 0)
    p2 = Player(2, "AI")
    h2 = Hero("Hero 2", 2, position=(0, 0), movement_points=10)
    p2.heroes.append(h2)

    p1 = Player(1, "Player") # Human player

    manager = GameManager(game_map, [p1, p2])
    ai = BasicAI(manager)

    # Execute AI turn
    ai.execute_turn(p2)

    # Hero should have moved toward (3, 3) and claimed it
    assert h2.position == (3, 3)
    assert poi.owner_id == 2
    assert poi.poi_id in p2.owned_pois
