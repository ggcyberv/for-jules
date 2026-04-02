import os
# Headless
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from engine.game_state import GameState
from world.world_generator import WorldGenerator
from party.party_manager import Party
from party.character import Character
from engine.save_manager import SaveManager

def test_save_load():
    seed = 42
    settings = {"world_size": (10, 10)}
    world_gen = WorldGenerator(seed, settings)
    grid = world_gen.generate()

    hero1 = Character("TestHero")
    party = Party(members=[hero1])
    state = GameState()
    state.initialize(grid, party, seed, world_gen.locations)
    state.turn = 10
    state.party.gold = 500

    save_path = "data/saves/test_save.sav"
    SaveManager.save_game(save_path)

    # Reset state
    state.turn = 1
    state.party.gold = 0

    # Load
    assert SaveManager.load_game(save_path)
    assert state.turn == 10
    assert state.party.gold == 500
    assert state.party.members[0].name == "TestHero"
    print("Save/Load test passed.")

if __name__ == "__main__":
    test_save_load()
