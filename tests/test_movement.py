import pytest
from engine.map import GameMap
from engine.navigation import astar, get_distance
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.manager import GameManager

def test_hex_neighbors():
    game_map = GameMap(10, 10)
    # Even row (y=0)
    neighbors = game_map.get_neighbors(1, 0)
    # Expected: (2,0), (0,0), (1,1), (0,1)
    assert len(neighbors) == 4
    assert (2,0) in neighbors
    assert (0,0) in neighbors
    assert (1,1) in neighbors
    assert (0,1) in neighbors

def test_get_distance_hex():
    # Distance between (0,0) and (2,0) is 2
    assert get_distance((0,0), (2,0)) == 2
    # Distance between (0,0) and (1,1) is 1?
    # (0,0) cube: x=0, z=0, y=0
    # (1,1) cube: y is 1, so y is odd row.
    # (1,1) cube: x = 1 - (1 - (1&1))//2 = 1 - 0 = 1. z = 1. y = -1 - 1 = -2.
    # (1,1) cube: x=1, z=1, y=-2.
    # Dist(0,0,0 and 1,-2,1) = max(1, 2, 1) = 2.
    # Wait, (0,0) and (1,1) are NOT neighbors in pointy-top odd-r.
    # Neighbors of (0,0) are (1,0), (-1,0), (0,1), (-1,1) in bounds: (1,0), (0,1).
    # So (1,1) should be distance 2.
    assert get_distance((0,0), (1,1)) == 2
    assert get_distance((0,0), (0,1)) == 1

def test_astar_hex():
    game_map = GameMap(10, 10)
    # Direct path
    path = astar(game_map, (0,0), (2,0))
    assert len(path) == 3

    path = astar(game_map, (0,0), (0,1))
    assert len(path) == 2

def test_move_hero_hex():
    game_map = GameMap(10, 10)
    p1 = Player(1, "P1")
    h1 = Hero("H1", 1, position=(0,0), movement_points=10)
    p1.heroes.append(h1)
    manager = GameManager(game_map, [p1])

    # Move to a neighbor
    manager.move_hero(h1, (1, 0))
    assert h1.position == (1, 0)
    assert h1.movement_points == 9
