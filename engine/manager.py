from typing import List, Dict, Optional, Any
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.map import GameMap
from engine.combat import resolve_combat, CombatResult
from engine.navigation import astar

class GameManager:
    def __init__(self, game_map: GameMap, players: List[Player]):
        self.game_map = game_map
        self.players = {p.player_id: p for p in players}
        self.player_ids = [p.player_id for p in players]
        self.current_player_idx = 0
        self.turn_number = 1
        self.win_threshold = 10
        self.win_streak_required = 3

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

    def next_turn(self):
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
            combat_result = resolve_combat(hero.army, poi.garrison, hero.owner_id, poi.owner_id or -1)

            self._apply_losses_by_id(hero.army, combat_result.army1_losses)
            self._apply_losses_by_id(poi.garrison, combat_result.army2_losses)

            if combat_result.winner_id == hero.owner_id:
                self._transfer_ownership(poi, hero.owner_id, old_owner_id)
                poi.garrison = []
                return {"type": "combat", "result": "win", "log": combat_result.log}
            else:
                return {"type": "combat", "result": "loss", "log": combat_result.log}
        else:
            self._transfer_ownership(poi, hero.owner_id, old_owner_id)
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

    def recruit_units(self, hero: Hero, poi: POI, unit_name: str, quantity: int) -> Dict[str, Any]:
        if poi.owner_id != hero.owner_id:
            return {"success": False, "message": "You don't own this POI"}

        if hero.position != poi.position:
            return {"success": False, "message": "Hero is not at the POI"}

        unit_type = next((u for u in poi.recruitable_units if u.name == unit_name), None)
        if not unit_type:
            return {"success": False, "message": "Unit type not recruitable here"}

        player = self.players[hero.owner_id]
        for res, cost in unit_type.cost.items():
            if player.resources.get(res, 0) < cost * quantity:
                return {"success": False, "message": f"Not enough {res}"}

        # Deduct resources
        for res, cost in unit_type.cost.items():
            player.resources[res] -= cost * quantity

        # Add units to hero
        existing_stack = next((s for s in hero.army if s.unit_type.name == unit_name), None)
        if existing_stack:
            existing_stack.quantity += quantity
        else:
            hero.army.append(Stack(unit_type, quantity))

        return {"success": True, "message": f"Recruited {quantity} {unit_name}"}

    def station_units(self, hero: Hero, poi: POI, unit_name: str, quantity: int, to_poi: bool) -> Dict[str, Any]:
        if poi.owner_id != hero.owner_id:
            return {"success": False, "message": "You don't own this POI"}

        if hero.position != poi.position:
            return {"success": False, "message": "Hero is not at the POI"}

        source, target = (hero.army, poi.garrison) if to_poi else (poi.garrison, hero.army)

        source_stack = next((s for s in source if s.unit_type.name == unit_name), None)
        if not source_stack or source_stack.quantity < quantity:
            return {"success": False, "message": "Not enough units in source"}

        # Move units
        source_stack.quantity -= quantity
        if source_stack.quantity == 0:
            source.remove(source_stack)

        target_stack = next((s for s in target if s.unit_type.name == unit_name), None)
        if target_stack:
            target_stack.quantity += quantity
        else:
            target.append(Stack(source_stack.unit_type, quantity))

        direction = "to POI" if to_poi else "to hero"
        return {"success": True, "message": f"Stationed {quantity} {unit_name} {direction}"}
