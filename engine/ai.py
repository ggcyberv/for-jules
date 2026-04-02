from typing import Optional, Tuple
from engine.models import Player, Hero, POI
from engine.manager import GameManager

class BasicAI:
    def __init__(self, manager: GameManager):
        self.manager = manager

    def execute_turn(self, player: Player):
        for hero in player.heroes:
            if hero.movement_points <= 0:
                continue

            target_poi = self._find_nearest_target(hero, player.player_id)
            if target_poi:
                # Try to move as close as possible to the POI
                self.manager.move_hero(hero, target_poi.position)

        # End turn
        self.manager.next_turn()

    def _find_nearest_target(self, hero: Hero, player_id: int) -> Optional[POI]:
        nearest_poi = None
        min_dist = float('inf')

        game_map = self.manager.game_map
        for x in range(game_map.width):
            for y in range(game_map.height):
                tile = game_map.get_tile(x, y)
                if tile and tile.poi and tile.poi.owner_id != player_id:
                    dist = max(abs(x - hero.position[0]), abs(y - hero.position[1]))
                    if dist < min_dist:
                        min_dist = dist
                        nearest_poi = tile.poi

        return nearest_poi
