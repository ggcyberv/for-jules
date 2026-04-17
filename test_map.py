import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from world.hex_grid import HexGrid
from world.world_generator import WorldGenerator

def test_infinite_map():
    seed = 12345
    settings = {"danger_level": 0.5}
    grid = HexGrid(chunk_size=10)
    gen = WorldGenerator(seed, settings)

    # Generate far away chunk
    q, r = 100, 100
    cq, cr = grid.get_chunk_coords(q, r)
    print(f"Generating chunk at {cq}, {cr}")
    gen.generate_chunk(grid, cq, cr)

    tile = grid.get_tile(q, r)
    if tile:
        print(f"Tile at ({q}, {r}) found: {tile.terrain_type}")
    else:
        print(f"Tile at ({q}, {r}) NOT found!")

    # Check if neighbor in another chunk can be generated
    nq, nr = 109, 109 # still in (10, 10) chunk if chunk_size=10?
    # Wait, chunk 10 is 100 to 109.
    tile2 = grid.get_tile(nq, nr)
    print(f"Tile at ({nq}, {nr}) found: {tile2 is not None}")

    nq2, nr2 = 110, 110 # chunk (11, 11)
    tile3 = grid.get_tile(nq2, nr2)
    print(f"Tile at ({nq2}, {nr2}) found (should be False): {tile3 is not None}")

    cq2, cr2 = grid.get_chunk_coords(nq2, nr2)
    gen.generate_chunk(grid, cq2, cr2)
    tile4 = grid.get_tile(nq2, nr2)
    print(f"Tile at ({nq2}, {nr2}) found after generation: {tile4 is not None}")

if __name__ == "__main__":
    test_infinite_map()
