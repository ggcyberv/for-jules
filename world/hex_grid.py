from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set

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
    visible: bool = False

class HexGrid:
    def __init__(self, chunk_size: int = 16):
        self.chunk_size = chunk_size
        self.tiles: Dict[Tuple[int, int], HexTile] = {}
        self.generated_chunks: Set[Tuple[int, int]] = set()

    def get_tile(self, q: int, r: int) -> Optional[HexTile]:
        return self.tiles.get((q, r))

    def add_tile(self, tile: HexTile):
        self.tiles[(tile.q, tile.r)] = tile

    def get_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        neighbors = []
        for dq, dr in directions:
            nq, nr = q + dq, r + dr
            # Infinite grid: neighbors might not exist yet but we return the coords
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

    def get_chunk_coords(self, q: int, r: int) -> Tuple[int, int]:
        cq = q // self.chunk_size
        cr = r // self.chunk_size
        return (cq, cr)
