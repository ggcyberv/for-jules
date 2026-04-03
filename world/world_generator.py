from typing import Dict, Any, List, Tuple
from world.hex_grid import HexGrid, HexTile
from engine.rng_manager import RNGManager
from world.location import Town, Dungeon, TownNode
from party.character import Character, Skill
from party.item import Weapon, Armor

class WorldGenerator:
    def __init__(self, seed: int, settings: Dict[str, Any]):
        self.base_seed = seed
        self.settings = settings
        self.locations: Dict[str, Any] = {}
        self.capitals = {
            "citizens": (0, 0),
            "bandits": (100, 100),
            "nomads": (-100, 50),
            "undead": (50, -100)
        }

    def generate_chunk(self, grid: HexGrid, cq: int, cr: int):
        if (cq, cr) in grid.generated_chunks:
            return

        chunk_seed = self.base_seed ^ (cq * 73856093) ^ (cr * 19349663)
        rng = RNGManager(chunk_seed)

        c_size = grid.chunk_size
        for q in range(cq * c_size, (cq + 1) * c_size):
            for r in range(cr * c_size, (cr + 1) * c_size):
                tile = HexTile(q, r)

                noise_val = rng.get_float()
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

                tile.danger_rating = rng.get_float() * self.settings.get("danger_level", 0.5)

                best_dist = 9999
                best_faction = None
                for faction_id, (cap_q, cap_r) in self.capitals.items():
                    d = HexGrid.distance(q, r, cap_q, cap_r)
                    if d < best_dist:
                        best_dist = d
                        best_faction = faction_id
                tile.faction_influence = best_faction

                # Use urbanization and loot_abundance settings
                urbanization = self.settings.get("urbanization", 0.4)
                loot_abundance = self.settings.get("loot_abundance", 0.5)

                if (q, r) != (0, 0) and rng.get_float() < (0.01 + loot_abundance * 0.03):
                    poi_id = f"loc_{q}_{r}"
                    tile.poi_id = poi_id
                    if rng.get_float() < urbanization:
                        town = Town(poi_id, f"Outpost {q},{r}", q, r)
                        # Add a recruit with backstory
                        recruit = Character(
                            f"Soldier {q}",
                            backstory=f"A veteran of the border wars near {q},{r}."
                        )
                        recruit.skills = [Skill("Defense", "Better shielding.")]
                        town.recruits = [recruit]
                        self.locations[poi_id] = town
                    else:
                        self.locations[poi_id] = Dungeon(poi_id, f"Ruins {q},{r}", q, r)

                grid.add_tile(tile)

        if cq == 0 and cr == 0:
            tile = grid.get_tile(0, 0)
            tile.terrain_type = "plains"
            tile.poi_id = "start_town"
            start_town = Town("start_town", "Riverfall", 0, 0)
            start_town.nodes = [
                TownNode("market", "Market", "Trade and buy supplies.", "market"),
                TownNode("healer", "Healer", "Heal your party.", "healer"),
                TownNode("guild", "Guild", "Find new companions.", "recruit")
            ]
            start_town.inventory = [Weapon("iron_sword", "Iron Sword", "Simple blade.", 50, 3)]
            recruit = Character("Brog", backstory="A former miner looking for glory.")
            recruit.skills = [Skill("Toughness", "Extra HP.")]
            start_town.recruits = [recruit]
            self.locations["start_town"] = start_town

        grid.generated_chunks.add((cq, cr))
