from typing import List, Dict, Optional, Any
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.map import GameMap
from engine.combat import resolve_combat, CombatResult
from engine.navigation import astar
from engine.world_sim import EventManager

class GameManager:
    def __init__(self, game_map: GameMap, players: List[Player]):
        self.game_map = game_map
        self.players = {p.player_id: p for p in players}
        self.player_ids = [p.player_id for p in players]
        self.current_player_idx = 0
        self.turn_number = 1
        self.win_threshold = 10
        self.win_streak_required = 3
        self.event_manager = EventManager()
        self.game_log: List[str] = []

        # Initial scan to populate owned_pois
        self._initialize_owned_pois()

    def _initialize_owned_pois(self):
        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                tile = self.game_map.get_tile(x, y)
                if tile and tile.poi and tile.poi.owner_id:
                    player = self.players.get(tile.poi.owner_id)
                    if player:
                        if tile.poi.poi_id not in player.owned_pois:
                            player.owned_pois.append(tile.poi.poi_id)

    @property
    def current_player(self) -> Player:
        return self.players[self.player_ids[self.current_player_idx]]

    def tick(self):
        event = self.event_manager.generate_random_event(self.turn_number)
        if event:
            self.game_log.append(f"EVENT: {event.description}")

    def next_turn(self):
        self.tick()
        self.current_player_idx = (self.current_player_idx + 1) % len(self.player_ids)
        if self.current_player_idx == 0:
            self.turn_number += 1

        # Start of turn logic
        player = self.current_player
        for hero in player.heroes:
            hero.movement_points = hero.max_movement_points

        # Collect resources and check win condition
        self._process_income(player)
        self._check_win_condition(player)

    def _process_income(self, player: Player):
        for poi_id in player.owned_pois:
            poi = self._get_poi_by_id(poi_id)
            if poi:
                for res, amount in poi.income.items():
                    player.resources[res] = player.resources.get(res, 0) + amount

    def _get_poi_by_id(self, poi_id: str) -> Optional[POI]:
        # This could be optimized further with a POI map if needed
        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                tile = self.game_map.get_tile(x, y)
                if tile and tile.poi and tile.poi.poi_id == poi_id:
                    return tile.poi
        return None

    def _check_win_condition(self, player: Player):
        total_control = 0
        for poi_id in player.owned_pois:
            poi = self._get_poi_by_id(poi_id)
            if poi:
                total_control += poi.control_value

        if total_control >= self.win_threshold:
            player.winning_streak += 1
        else:
            player.winning_streak = 0

    def move_hero(self, hero: Hero, target_pos: tuple) -> Dict[str, Any]:
        path = astar(self.game_map, hero.position, target_pos)
        if not path:
            return {"success": False, "message": "No path found"}

        actual_path = []
        cost_spent = 0
        for pos in path[1:]:
            tile = self.game_map.get_tile(pos[0], pos[1])
            if cost_spent + tile.movement_cost <= hero.movement_points:
                cost_spent += tile.movement_cost
                actual_path.append(pos)
            else:
                break

        if not actual_path:
            return {"success": False, "message": "Not enough movement points"}

        final_pos = actual_path[-1]
        hero.position = final_pos
        hero.movement_points -= cost_spent

        tile = self.game_map.get_tile(final_pos[0], final_pos[1])
        interaction_result = None
        if tile.poi:
            interaction_result = self._interact_with_poi(hero, tile.poi)

        return {
            "success": True,
            "message": f"Hero moved to {final_pos}",
            "cost": cost_spent,
            "interaction": interaction_result
        }

    def _interact_with_poi(self, hero: Hero, poi: POI) -> Dict[str, Any]:
        if poi.owner_id == hero.owner_id:
            return {"type": "visit", "message": f"Visited friendly {poi.poi_type}"}

        old_owner_id = poi.owner_id
        if poi.garrison:
            combat_result = resolve_combat(hero.party, poi.garrison, hero.owner_id, poi.owner_id or -1)

            # Note: _apply_losses_by_id will need update for Character objects or we handle it here
            # For now, let's assume resolve_combat handles it or we'll update it later

            if combat_result.winner_id == hero.owner_id:
                self._transfer_ownership(poi, hero.owner_id, old_owner_id)
                self.game_log.append(f"COMBAT: {hero.name} defeated garrison at {poi.poi_type} {poi.poi_id}")
                poi.garrison = []
                # Award XP
                self._award_xp(hero, combat_result.xp_reward)
                return {"type": "combat", "result": "win", "log": combat_result.log, "xp_gained": combat_result.xp_reward}
            else:
                self.game_log.append(f"COMBAT: {hero.name} was defeated at {poi.poi_type} {poi.poi_id}")
                return {"type": "combat", "result": "loss", "log": combat_result.log}
        else:
            self._transfer_ownership(poi, hero.owner_id, old_owner_id)
            self.game_log.append(f"CLAIM: {hero.name} claimed {poi.poi_type} {poi.poi_id}")
            return {"type": "claim", "message": f"Claimed {poi.poi_type}"}

    def _transfer_ownership(self, poi: POI, new_owner_id: int, old_owner_id: Optional[int]):
        if old_owner_id:
            old_player = self.players.get(old_owner_id)
            if old_player and poi.poi_id in old_player.owned_pois:
                old_player.owned_pois.remove(poi.poi_id)

        poi.owner_id = new_owner_id
        new_player = self.players.get(new_owner_id)
        if new_player and poi.poi_id not in new_player.owned_pois:
            new_player.owned_pois.append(poi.poi_id)

    def _apply_losses_by_id(self, army: List[Stack], losses: Dict[str, int]):
        for stack in army:
            if stack.stack_id in losses:
                stack.quantity -= losses[stack.stack_id]
        army[:] = [s for s in army if s.quantity > 0]

    def _award_xp(self, hero: Hero, amount: int):
        # In D&D mode, XP is usually split among party members
        if not hero.party: return
        share = amount // len(hero.party)
        for char in hero.party:
            char.experience += share
            while char.experience >= (char.level * 1000):
                char.experience -= (char.level * 1000)
                char.level += 1
                char.max_hp += 10
                char.current_hp = char.max_hp

    def recruit_units(self, hero: Hero, poi: POI, unit_name: str, quantity: int) -> Dict[str, Any]:
        return {"success": False, "message": "Unit recruitment disabled in D&D mode. Look for NPCs to join your party!"}

    def station_units(self, hero: Hero, poi: POI, unit_name: str, quantity: int, to_poi: bool) -> Dict[str, Any]:
        return {"success": False, "message": "Unit stationing disabled in D&D mode."}

    def _apply_losses_by_id(self, army: List[Stack], losses: Dict[str, int]):
        # This is now handled by character HP in tactical combat
        pass

    def get_render_state(self) -> Dict[str, Any]:
        tiles = []
        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                tile = self.game_map.get_tile(x, y)
                if tile:
                    poi_data = None
                    if tile.poi:
                        poi_data = {
                            "type": tile.poi.poi_type,
                            "owner": tile.poi.owner_id
                        }
                    tiles.append({
                        "x": x, "y": y,
                        "terrain": tile.terrain_type,
                        "poi": poi_data,
                        "discovered": tile.discovered
                    })

        heroes = []
        party_info = []
        for player in self.players.values():
            for hero in player.heroes:
                heroes.append({
                    "x": hero.position[0],
                    "y": hero.position[1],
                    "owner": hero.owner_id
                })
                if player.player_id == self.player_ids[0]: # Assuming p1 is player
                    for char in hero.party:
                        party_info.append({
                            "name": char.name,
                            "class": char.char_class,
                            "hp": char.current_hp,
                            "max_hp": char.max_hp,
                            "level": char.level
                        })

        return {
            "tiles": tiles,
            "heroes": heroes,
            "party_info": party_info,
            "log": self.game_log
        }
