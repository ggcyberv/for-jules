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
    notes: List[str] = field(default_factory=list)
    discovered: bool = False

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

    def discover_area(self, x: int, y: int, radius: int):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                # Simple distance check for hex-like radius (Manhattan in axial would be better but this is fine for now)
                dist = max(abs(dx), abs(dy), abs(dx + dy))
                if dist <= radius:
                    tile = self.get_tile(x + dx, y + dy)
                    if tile:
                        tile.discovered = True

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Get 6 hexagonal neighbors using 'pointy-topped odd-r' offset coordinates.
        """
        neighbors = []
        if y % 2 == 0:
            # Even row: (x+1,y), (x-1,y), (x,y-1), (x-1,y-1), (x,y+1), (x-1,y+1)
            dirs = [(+1, 0), (-1, 0), (0, -1), (-1, -1), (0, +1), (-1, +1)]
        else:
            # Odd row: (x+1,y), (x-1,y), (x,y-1), (x+1,y-1), (x,y+1), (x+1,y+1)
            dirs = [(+1, 0), (-1, 0), (0, -1), (+1, -1), (0, +1), (+1, +1)]

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))

        return neighbors
