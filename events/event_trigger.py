from typing import Dict, Any, List
from engine.game_state import GameState
from engine.event_bus import event_bus

class EventTrigger:
    @staticmethod
    def check_enter_hex(q: int, r: int):
        state = GameState()
        tile = state.world.get_tile(q, r)

        # In Milestone 1, we simulate a random encounter chance
        if tile.danger_rating > 0.85: # Reduced chance for demo
            event_bus.publish("random_encounter", q=q, r=r)

        # Check for POIs or specific hex discovery
        if not tile.discovered:
            tile.discovered = True
            event_bus.publish("hex_discovered", q=q, r=r)

        if tile.poi_id:
            event_bus.publish("enter_location", poi_id=tile.poi_id)

        # Example story event on specific hex
        if q == 2 and r == 2:
            event_bus.publish("trigger_story_event", event_id="crypt_whispers_01")
