import pytest
from engine.map import GameMap
from engine.navigation import astar, get_distance
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.manager import GameManager

def test_get_distance():
    assert get_distance((0,0), (3,4)) == 4

def test_astar_simple():
    game_map = GameMap(10, 10)
    start = (0, 0)
    end = (2, 2)
    path = astar(game_map, start, end)

    assert path is not None
    assert path[0] == start
    assert path[-1] == end
    assert len(path) == 3

def test_move_hero_success():
    game_map = GameMap(10, 10)
    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(0,0), movement_points=10)
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    result = manager.move_hero(h1, (5, 5))

    assert result["success"] == True
    assert h1.position == (5, 5)
    assert h1.movement_points == 5

def test_move_hero_partial():
    game_map = GameMap(10, 10)
    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(0,0), movement_points=3)
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    result = manager.move_hero(h1, (5, 5))

    assert result["success"] == True
    assert h1.position == (3, 3)
    assert h1.movement_points == 0

def test_move_hero_no_mp():
    game_map = GameMap(10, 10)
    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(0,0), movement_points=0)
    p1.heroes.append(h1)

    manager = GameManager(game_map, [p1])

    result = manager.move_hero(h1, (5, 5))

    assert result["success"] == False
    assert h1.position == (0, 0)
