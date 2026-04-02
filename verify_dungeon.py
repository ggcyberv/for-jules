from world.dungeon_generator import DungeonGenerator

def test_dungeon():
    gen = DungeonGenerator(1234)
    dungeon = gen.generate(40, 20, num_rooms=5)

    print(f"Dungeon: {dungeon.width}x{dungeon.height}")
    print(f"Start: {dungeon.start_pos}, Exit: {dungeon.exit_pos}")

    # Print a small representation
    for y in range(dungeon.height):
        line = ""
        for x in range(dungeon.width):
            tile = dungeon.get_tile(x, y)
            if (x, y) == dungeon.start_pos: line += "S"
            elif (x, y) == dungeon.exit_pos: line += "E"
            elif tile.is_wall: line += "#"
            else: line += "."
        print(line)

if __name__ == "__main__":
    test_dungeon()
