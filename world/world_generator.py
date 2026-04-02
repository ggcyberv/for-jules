from typing import Dict, Any, List
from world.hex_grid import HexGrid
from engine.rng_manager import RNGManager
from world.location import Town, Dungeon, TownNode
from party.character import Character

class WorldGenerator:
    def __init__(self, seed: int, settings: Dict[str, Any]):
        self.rng = RNGManager(seed)
        self.settings = settings
        self.width, self.height = settings.get("world_size", (100, 80))
        self.locations: Dict[str, Any] = {}

    def generate(self) -> HexGrid:
        grid = HexGrid(self.width, self.height)

        # Simple procedural generation logic
        for (q, r), tile in grid.tiles.items():
            noise_val = self.rng.get_float()
            if noise_val < 0.1:
                tile.terrain_type = "mountain"
                tile.movement_cost = 3.0
            elif noise_val < 0.3:
                tile.terrain_type = "forest"
                tile.movement_cost = 1.5
            elif noise_val < 0.4:
                tile.terrain_type = "water"
                tile.movement_cost = 5.0
            else:
                tile.terrain_type = "plains"
                tile.movement_cost = 1.0

            # Initial danger rating
            tile.danger_rating = self.rng.get_float() * self.settings.get("danger_level", 0.5)

        # Place Faction Capitals
        capitals = {
            "citizens": (0, 0),
            "bandits": (self.width - 1, self.height - 1)
        }

        # Place a starting Town at citizens capital
        start_tile = grid.get_tile(0, 0)
        start_tile.terrain_type = "plains"
        start_tile.movement_cost = 1.0
        start_tile.poi_id = "start_town"

        start_town = Town(poi_id="start_town", name="Riverfall", q=0, r=0)
        start_town.nodes = [
            TownNode("market", "Market", "Trade and buy supplies.", "market"),
            TownNode("tavern", "Tavern", "Rest and hear rumors.", "tavern"),
            TownNode("healer", "Healer", "Heal your party for gold.", "healer"),
            TownNode("guild", "Guild Hall", "Recruit new members.", "recruit")
        ]
        start_town.recruits = [Character("Brog", attack=14, defense=12, speed=4)]
        start_town.faction_id = "citizens"
        self.locations["start_town"] = start_town

        # Faction Territories (Voronoi)
        for (q, r), tile in grid.tiles.items():
            best_dist = 9999
            best_faction = None
            for faction_id, (cq, cr) in capitals.items():
                d = grid.distance(q, r, cq, cr)
                if d < best_dist:
                    best_dist = d
                    best_faction = faction_id
            tile.faction_influence = best_faction

        # Randomly place some Dungeons
        dungeon_count = 5
        all_coords = list(grid.tiles.keys())
        self.rng.shuffle(all_coords)

        placed = 0
        for q, r in all_coords:
            if (q, r) == (0, 0): continue
            tile = grid.get_tile(q, r)
            if tile.terrain_type != "water":
                poi_id = f"dungeon_{placed}"
                tile.poi_id = poi_id
                self.locations[poi_id] = Dungeon(poi_id=poi_id, name=f"Lost Crypt {placed}", q=q, r=r)
                placed += 1
                if placed >= dungeon_count: break

        return grid
