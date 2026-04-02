from engine.game_state import GameState
from world.dungeon_generator import DungeonGenerator

def test_fov():
    gen = DungeonGenerator(1)
    dungeon = gen.generate(20, 20)
    state = GameState()
    state.active_dungeon = dungeon
    state.dungeon_pos = dungeon.start_pos

    state.compute_fov(radius=3)

    # Check start tile is visible
    start_tile = dungeon.get_tile(dungeon.start_pos[0], dungeon.start_pos[1])
    assert start_tile.visible == True
    assert start_tile.explored == True

    # Check distant tile is not visible
    far_tile = dungeon.get_tile(0, 0)
    assert far_tile.visible == False
    print("FOV test passed.")

if __name__ == "__main__":
    test_fov()
