from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

@dataclass
class HexTile:
    q: int
    r: int
    terrain_type: str = "plains"
    movement_cost: float = 1.0
    poi_id: Optional[str] = None
    danger_rating: float = 0.0
    faction_influence: Optional[str] = None
    discovered: bool = False

class HexGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: Dict[Tuple[int, int], HexTile] = {}
        for r in range(height):
            r_offset = r // 2
            for q in range(-r_offset, width - r_offset):
                self.tiles[(q, r)] = HexTile(q, r)

    def get_tile(self, q: int, r: int) -> Optional[HexTile]:
        return self.tiles.get((q, r))

    def get_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        neighbors = []
        for dq, dr in directions:
            nq, nr = q + dq, r + dr
            if (nq, nr) in self.tiles:
                neighbors.append((nq, nr))
        return neighbors

    @staticmethod
    def axial_to_cube(q: int, r: int) -> Tuple[int, int, int]:
        return (q, r, -q - r)

    @staticmethod
    def distance(q1: int, r1: int, q2: int, r2: int) -> int:
        c1 = HexGrid.axial_to_cube(q1, r1)
        c2 = HexGrid.axial_to_cube(q2, r2)
        return (abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])) // 2
