from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from engine.models import POI

@dataclass
class Tile:
    x: int
    y: int
    terrain_type: str = "plains"
    movement_cost: float = 1.0
    poi: Optional[POI] = None

class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: List[List[Tile]] = [
            [Tile(x, y) for y in range(height)]
            for x in range(width)
        ]

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None

    def set_poi(self, poi: POI):
        x, y = poi.position
        tile = self.get_tile(x, y)
        if tile:
            tile.poi = poi
