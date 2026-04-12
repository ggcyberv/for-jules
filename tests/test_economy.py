import pytest
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.map import GameMap
from engine.manager import GameManager

def test_recruitment_disabled():
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    game_map = GameMap(10, 10)
    town = POI("town1", "town", (1, 1), 5, owner_id=1, recruitable_units=[swordsman])
    game_map.set_poi(town)

    p1 = Player(1, "Player 1", resources={"gold": 500})
    h1 = Hero("Hero 1", 1, position=(1, 1))
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    # Recruit should fail in D&D mode
    result = manager.recruit_units(h1, town, "Swordsman", 3)
    assert result["success"] == False

def test_stationing_disabled():
    game_map = GameMap(10, 10)
    town = POI("town1", "town", (1, 1), 5, owner_id=1)
    game_map.set_poi(town)

    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(1, 1))
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    result = manager.station_units(h1, town, "Swordsman", 4, to_poi=True)
    assert result["success"] == False
