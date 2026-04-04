import json
import pickle
import os
from engine.game_state import GameState

class SaveManager:
    @staticmethod
    def save_game(filepath: str):
        state = GameState()
        data = {
            "seed": state.seed,
            "turn": state.turn,
            "global_flags": state.global_flags,
            "world_facts": state.world_facts,
            "timed_events": state.timed_events,
            "ironman": state.ironman,
            "consecutive_wait_turns": state.consecutive_wait_turns,
            "last_pos": state.last_pos,
            "current_weather": state.current_weather,
            "active_dungeon_id": state.active_dungeon_id,
            "dungeon_pos": state.dungeon_pos,
            # Pickled complex objects
            "world": pickle.dumps(state.world),
            "party": pickle.dumps(state.party),
            "quest_manager": pickle.dumps(state.quest_manager),
            "lore_manager": pickle.dumps(state.lore_manager),
            "faction_system": pickle.dumps(state.faction_system),
            "npc_parties": pickle.dumps(state.npc_parties),
            "locations": pickle.dumps(state.locations),
            "active_dungeon": pickle.dumps(state.active_dungeon)
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def load_game(filepath: str):
        if not os.path.exists(filepath):
            return False

        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        state = GameState()
        state.seed = data["seed"]
        state.turn = data["turn"]
        state.global_flags = data["global_flags"]
        state.world_facts = data.get("world_facts", [])
        state.timed_events = data.get("timed_events", [])
        state.ironman = data.get("ironman", False)
        state.consecutive_wait_turns = data.get("consecutive_wait_turns", 0)
        state.last_pos = data.get("last_pos", (0, 0))
        state.current_weather = data.get("current_weather", "Clear")
        state.active_dungeon_id = data.get("active_dungeon_id")
        state.dungeon_pos = data.get("dungeon_pos", (0, 0))

        state.world = pickle.loads(data["world"])
        state.party = pickle.loads(data["party"])
        state.quest_manager = pickle.loads(data["quest_manager"])
        state.lore_manager = pickle.loads(data["lore_manager"])
        state.faction_system = pickle.loads(data["faction_system"])
        state.npc_parties = pickle.loads(data["npc_parties"])
        state.locations = pickle.loads(data["locations"])
        state.active_dungeon = pickle.loads(data["active_dungeon"])
        return True
