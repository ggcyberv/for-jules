from typing import Dict, Any, List
from engine.game_state import GameState
from engine.event_bus import event_bus

class EventTrigger:
    @staticmethod
    def check_enter_hex(q: int, r: int):
        state = GameState()

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

        if tile.danger_rating > 0.85:
            event_bus.publish("random_encounter", q=q, r=r)

        if tile.poi_id:
            event_bus.publish("enter_location", poi_id=tile.poi_id)

        if q == 2 and r == 2:
            event_bus.publish("trigger_story_event", event_id="crypt_whispers_01")
