import random
import json
import os
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
    trap_id: Optional[str] = None
    has_loot: bool = False
    enemies: List[str] = field(default_factory=list)

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
        self.room_templates = []
        self._load_templates("data/dungeon_rooms")

    def _load_templates(self, directory: str):
        if not os.path.exists(directory): return
        for fn in os.listdir(directory):
            if fn.endswith(".json"):
                with open(os.path.join(directory, fn), "r") as f:
                    self.room_templates.append(json.load(f))

    def generate(self, width: int, height: int, num_rooms: int = 10) -> DungeonMap:
        dungeon = DungeonMap(width, height)
        for y in range(height):
            for x in range(width):
                dungeon.tiles[(x, y)] = DungeonTile(x, y, is_wall=True)

        rooms = []
        for _ in range(num_rooms):
            if self.room_templates and self.rng.get_float() < 0.5:
                template = self.rng.choice(self.room_templates)
                w, h = template["width"], template["height"]
            else:
                w = self.rng.get_int(3, 6)
                h = self.rng.get_int(3, 6)
                template = None

            x = self.rng.get_int(1, width - w - 1)
            y = self.rng.get_int(1, height - h - 1)

            intersects = False
            for other in rooms:
                if (x < other[0] + other[2] and x + w > other[0] and
                    y < other[1] + other[3] and y + h > other[1]):
                    intersects = True
                    break

            if not intersects:
                self._create_room(dungeon, x, y, w, h, template)

                # Randomly place loot
                if self.rng.get_float() < 0.3:
                    lx = self.rng.get_int(x, x + w - 1)
                    ly = self.rng.get_int(y, y + h - 1)
                    ltile = dungeon.get_tile(lx, ly)
                    if ltile and not ltile.is_wall:
                        ltile.has_loot = True

                # Randomly place traps in the room
                for _ in range(self.rng.get_int(1, 3)):
                    tx = self.rng.get_int(x, x + w - 1)
                    ty = self.rng.get_int(y, y + h - 1)
                    tile = dungeon.get_tile(tx, ty)
                    if tile and not tile.is_wall:
                        tile.trap_id = "poison_dart" if self.rng.get_float() < 0.5 else "spike_trap"
                if not rooms:
                    dungeon.start_pos = (x + w // 2, y + h // 2)
                else:
                    px, py, pw, ph = rooms[-1]
                    self._create_h_tunnel(dungeon, px + pw // 2, x + w // 2, py + ph // 2)
                    self._create_v_tunnel(dungeon, py + ph // 2, y + h // 2, x + w // 2)

                    # Add enemies to new rooms (except starting room)
                    if self.rng.get_float() < 0.6:
                        ex = self.rng.get_int(x, x + w - 1)
                        ey = self.rng.get_int(y, y + h - 1)
                        etile = dungeon.get_tile(ex, ey)
                        if etile and not etile.is_wall:
                            etile.enemies = [self.rng.choice(["orc", "skeleton", "bandit"])]
                rooms.append((x, y, w, h))

        if rooms:
            lr = rooms[-1]
            dungeon.exit_pos = (lr[0] + lr[2] // 2, lr[1] + lr[3] // 2)
        return dungeon

    def _create_room(self, dungeon, x, y, w, h, template):
        for rx in range(x, x + w):
            for ry in range(y, y + h):
                tile = dungeon.get_tile(rx, ry)
                if not tile: continue
                if template:
                    char = template["tiles"][ry - y][rx - x]
                    tile.is_wall = (char == "#")
                else:
                    tile.is_wall = False

    def _create_h_tunnel(self, dungeon, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            tile = dungeon.get_tile(x, y)
            if tile: tile.is_wall = False

    def _create_v_tunnel(self, dungeon, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            tile = dungeon.get_tile(x, y)
            if tile: tile.is_wall = False
