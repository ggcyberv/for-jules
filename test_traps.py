from world.dungeon_generator import DungeonGenerator

def test_traps():
    gen = DungeonGenerator(seed=42)
    dungeon = gen.generate(width=20, height=20, num_rooms=5)

    trap_count = 0
    for tile in dungeon.tiles.values():
        if tile.trap_id:
            print(f"Trap found at ({tile.x}, {tile.y}): {tile.trap_id}")
            trap_count += 1

    if trap_count > 0:
        print(f"SUCCESS: {trap_count} traps placed.")
    else:
        print("FAILED: No traps placed.")

if __name__ == "__main__":
    test_traps()
