import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from engine.rng_manager import RNGManager

@dataclass
class DungeonTile:
    x: int
    y: int
    is_wall: bool = True
    explored: bool = False
    visible: bool = False

@dataclass
class DungeonMap:
    width: int
    height: int
    tiles: Dict[Tuple[int, int], DungeonTile] = field(default_factory=dict)
    start_pos: Tuple[int, int] = (0, 0)
    exit_pos: Tuple[int, int] = (0, 0)

    def get_tile(self, x: int, y: int) -> Optional[DungeonTile]:
        return self.tiles.get((x, y))

class DungeonGenerator:
    def __init__(self, seed: int):
        self.rng = RNGManager(seed)

    def generate(self, width: int, height: int, num_rooms: int = 10, min_room_size: int = 3, max_room_size: int = 6) -> DungeonMap:
        dungeon = DungeonMap(width, height)
        for y in range(height):
            for x in range(width):
                dungeon.tiles[(x, y)] = DungeonTile(x, y, is_wall=True)

        rooms = []
        for _ in range(num_rooms):
            w = self.rng.get_int(min_room_size, max_room_size)
            h = self.rng.get_int(min_room_size, max_room_size)
            x = self.rng.get_int(1, width - w - 1)
            y = self.rng.get_int(1, height - h - 1)

            new_room = pygame_rect_stub(x, y, w, h) # Using a simple rect logic

            # Check for overlaps
            intersects = False
            for other_room in rooms:
                if (x < other_room[0] + other_room[2] and x + w > other_room[0] and
                    y < other_room[1] + other_room[3] and y + h > other_room[1]):
                    intersects = True
                    break

            if not intersects:
                self._create_room(dungeon, x, y, w, h)
                if not rooms:
                    dungeon.start_pos = (x + w // 2, y + h // 2)
                else:
                    prev_x, prev_y, prev_w, prev_h = rooms[-1]
                    self._create_h_tunnel(dungeon, prev_x + prev_w // 2, x + w // 2, prev_y + prev_h // 2)
                    self._create_v_tunnel(dungeon, prev_y + prev_h // 2, y + h // 2, x + w // 2)

                rooms.append((x, y, w, h))

        if rooms:
            last_room = rooms[-1]
            dungeon.exit_pos = (last_room[0] + last_room[2] // 2, last_room[1] + last_room[3] // 2)

        return dungeon

    def _create_room(self, dungeon: DungeonMap, x: int, y: int, w: int, h: int):
        for rx in range(x, x + w):
            for ry in range(y, y + h):
                tile = dungeon.get_tile(rx, ry)
                if tile:
                    tile.is_wall = False

    def _create_h_tunnel(self, dungeon: DungeonMap, x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            tile = dungeon.get_tile(x, y)
            if tile:
                tile.is_wall = False

    def _create_v_tunnel(self, dungeon: DungeonMap, y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            tile = dungeon.get_tile(x, y)
            if tile:
                tile.is_wall = False

def pygame_rect_stub(x, y, w, h):
    return (x, y, w, h)
