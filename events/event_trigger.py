from typing import Dict, Any, List
from engine.game_state import GameState
from engine.event_bus import event_bus

class EventTrigger:
    @staticmethod
    def check_enter_hex(q: int, r: int, last_q: int = None, last_r: int = None):
        state = GameState()

        # Check border crossing
        if last_q is not None:
            last_tile = state.world.get_tile(last_q, last_r)
            curr_tile = state.world.get_tile(q, r)
            if last_tile and curr_tile and last_tile.faction_influence != curr_tile.faction_influence:
                event_bus.publish("trigger_story_event", event_id="border_crossing")

        # Signal to generate chunks around current position
        event_bus.publish("request_generation", q=q, r=r)

        # Discover tiles in a small radius (2 hexes)
        for dq in range(-2, 3):
            for dr in range(max(-2, -dq - 2), min(2, -dq + 2) + 1):
                nq, nr = q + dq, r + dr
                ntile = state.world.get_tile(nq, nr)
                if ntile:
                    if not ntile.discovered:
                        ntile.discovered = True
                    if dq == 0 and dr == 0:
                        # Re-publish discovery for the specific tile we just entered
                        pass

        tile = state.world.get_tile(q, r)
        if not tile: return

        if state.party and state.party.forced_march:
            event_bus.publish("trigger_story_event", event_id="forced_march_exhaustion")

        if tile.danger_rating > 0.85:
            event_bus.publish("random_encounter", q=q, r=r)

        if tile.poi_id:
            event_bus.publish("enter_location", poi_id=tile.poi_id)

        if q == 2 and r == 2:
            event_bus.publish("trigger_story_event", event_id="crypt_whispers_01")

    @staticmethod
    def check_wait():
        state = GameState()
        if state.consecutive_wait_turns >= 2:
            event_bus.publish("trigger_story_event", event_id="whispers_from_well")

    @staticmethod
    def check_time():
        state = GameState()
        if state.turn == 47:
            event_bus.publish("trigger_story_event", event_id="traveling_merchant_spawn")
