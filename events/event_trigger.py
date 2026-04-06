from typing import Dict, Any, List
from engine.game_state import GameState
from engine.event_bus import event_bus

class EventTrigger:
    @staticmethod
    def check_trigger(trigger_type: str, context: Dict[str, Any]):
        """Publishes a request for a random event of a specific type."""
        event_bus.publish("request_random_event", trigger_type=trigger_type, context=context)

    @staticmethod
    def check_enter_hex(q: int, r: int, last_q: int = None, last_r: int = None):
        state = GameState()
        import random
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

        tile = state.world.get_tile(q, r)
        if not tile: return

        context = {
            "q": q, "r": r,
            "terrain": tile.terrain_type,
            "danger": tile.danger_rating,
            "faction": tile.faction_influence,
            "poi_id": tile.poi_id
        }

        # Check border crossing (Trigger Type B - NPC/News/Borders)
        if last_q is not None:
            last_tile = state.world.get_tile(last_q, last_r)
            if last_tile and last_tile.faction_influence != tile.faction_influence:
                EventTrigger.check_trigger("b", context)

        # Forced March Check
        if state.party and state.party.forced_march:
            EventTrigger.check_trigger("a", context) # Could be a specific exhaustion event

        # Random Encounter Check
        if tile.danger_rating > 0.85:
            event_bus.publish("random_encounter", q=q, r=r)

        if tile.poi_id:
            event_bus.publish("enter_location", poi_id=tile.poi_id)

        # Generic "Enter Hex" trigger (Category A) - 5% chance
        if random.random() < 0.05:
            EventTrigger.check_trigger("a", context)

    @staticmethod
    def check_wait():
        state = GameState()
        import random
        tile = state.world.get_tile(state.party.q, state.party.r)
        context = {
            "q": state.party.q, "r": state.party.r,
            "terrain": tile.terrain_type if tile else "plains",
            "danger": tile.danger_rating if tile else 0.0,
            "faction": tile.faction_influence if tile else "neutral"
        }
        # Category C - Wait/Time
        # Stayed for prolonged time: every AP after the first 2 has a 3% chance
        if state.ap_spent_in_hex > 2:
            if random.random() < 0.03:
                EventTrigger.check_trigger("c", context)

    @staticmethod
    def check_time():
        state = GameState()
        tile = state.world.get_tile(state.party.q, state.party.r)
        context = {
            "q": state.party.q, "r": state.party.r,
            "terrain": tile.terrain_type if tile else "plains",
            "danger": tile.danger_rating if tile else 0.0,
            "faction": tile.faction_influence if tile else "neutral",
            "turn": state.turn
        }
        # Category C - Wait/Time (Global ticks)
        # EventTrigger.check_trigger("c", context)
        pass

    @staticmethod
    def check_after_combat():
        state = GameState()
        import random
        tile = state.world.get_tile(state.party.q, state.party.r)
        context = {
            "q": state.party.q, "r": state.party.r,
            "terrain": tile.terrain_type if tile else "plains",
            "danger": tile.danger_rating if tile else 0.0,
            "faction": tile.faction_influence if tile else "neutral"
        }
        # After fight - 8% chance
        if random.random() < 0.08:
            EventTrigger.check_trigger("b", context) # Use Category B for post-combat news/NPCs? Or maybe Category F.

    @staticmethod
    def check_leave_hex(q, r):
        state = GameState()
        tile = state.world.get_tile(q, r)
        context = {
            "q": q, "r": r,
            "terrain": tile.terrain_type if tile else "plains",
            "danger": tile.danger_rating if tile else 0.0,
            "faction": tile.faction_influence if tile else "neutral"
        }
        # Category E - Leaving
        EventTrigger.check_trigger("e", context)
