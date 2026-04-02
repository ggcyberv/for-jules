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
            # For simplicity in Milestone 1, we pickle the complex objects
            "world": pickle.dumps(state.world),
            "party": pickle.dumps(state.party)
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
        state.world = pickle.loads(data["world"])
        state.party = pickle.loads(data["party"])
        return True
