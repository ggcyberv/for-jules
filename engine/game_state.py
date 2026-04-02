from typing import Optional, Dict, Any
from world.hex_grid import HexGrid
from party.party_manager import Party
from world.faction_system import FactionSystem

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
        return cls._instance

    def initialize(self, world: HexGrid, party: Party, seed: int, locations: Dict[str, Any]):
        self.world = world
        self.party = party
        self.seed = seed
        self.turn = 1
        self.global_flags = {}
        self.locations = locations
        self.faction_system = FactionSystem()

    def advance_turn(self):
        self.turn += 1
        if self.party:
            self.party.rest() # Reset AP and consume food every turn for now
