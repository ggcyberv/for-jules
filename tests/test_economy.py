import pytest
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.map import GameMap
from engine.manager import GameManager

def test_recruitment():
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    game_map = GameMap(10, 10)
    town = POI("town1", "town", (1, 1), 5, owner_id=1, recruitable_units=[swordsman])
    game_map.set_poi(town)

    p1 = Player(1, "Player 1", resources={"gold": 500})
    h1 = Hero("Hero 1", 1, position=(1, 1))
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    # Recruit 3 swordsmen
    result = manager.recruit_units(h1, town, "Swordsman", 3)

    assert result["success"] == True
    assert p1.resources["gold"] == 200
    assert len(h1.army) == 1
    assert h1.army[0].unit_type.name == "Swordsman"
    assert h1.army[0].quantity == 3

def test_stationing():
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    game_map = GameMap(10, 10)
    town = POI("town1", "town", (1, 1), 5, owner_id=1)
    game_map.set_poi(town)

    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(1, 1), army=[Stack(swordsman, 10, "s1")])
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    # Station 4 units to POI
    result = manager.station_units(h1, town, "Swordsman", 4, to_poi=True)

    assert result["success"] == True
    assert h1.army[0].quantity == 6
    assert len(town.garrison) == 1
    assert town.garrison[0].quantity == 4

    # Move back to hero
    result = manager.station_units(h1, town, "Swordsman", 2, to_poi=False)
    assert result["success"] == True
    assert h1.army[0].quantity == 8
    assert town.garrison[0].quantity == 2
