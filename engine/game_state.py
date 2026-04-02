from typing import Optional, Dict, Any, Tuple
from world.hex_grid import HexGrid
from party.party_manager import Party
from world.faction_system import FactionSystem
from world.dungeon_generator import DungeonMap

class GameState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance.world: Optional[HexGrid] = None
            cls._instance.party: Optional[Party] = None
            cls._instance.turn: int = 1
            cls._instance.seed: int = 0
            cls._instance.global_flags: Dict[str, Any] = {}
            cls._instance.locations: Dict[str, Any] = {}
            cls._instance.faction_system: Optional[FactionSystem] = None
            cls._instance.active_dungeon: Optional[DungeonMap] = None
            cls._instance.dungeon_pos: Tuple[int, int] = (0, 0)
        return cls._instance

    def initialize(self, world: HexGrid, party: Party, seed: int, locations: Dict[str, Any]):
        self.world = world
        self.party = party
        self.seed = seed
        self.turn = 1
        self.global_flags = {}
        self.locations = locations
        self.faction_system = FactionSystem()
        self.active_dungeon = None

    def advance_turn(self):
        self.turn += 1
        if self.party:
            self.party.rest() # Reset AP and consume food every turn for now

    def compute_fov(self, radius: int = 5):
        if not self.active_dungeon: return

        # Reset visibility
        for tile in self.active_dungeon.tiles.values():
            tile.visible = False

        cx, cy = self.dungeon_pos
        for x in range(cx - radius, cx + radius + 1):
            for y in range(cy - radius, cy + radius + 1):
                dist = (x - cx)**2 + (y - cy)**2
                if dist <= radius**2:
                    tile = self.active_dungeon.get_tile(x, y)
                    if tile:
                        tile.visible = True
                        tile.explored = True
