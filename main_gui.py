import pygame
import sys
import math
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.map import GameMap
from engine.manager import GameManager
from engine.graphics import Renderer
from engine.ai import BasicAI

from engine.models import Character, Stats

def create_game():
    # Define unit types
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    archer = UnitType("Archer", 6, 3, 15, 2, 6, 6, {"gold": 120}, 12, 1)
    knight = UnitType("Knight", 10, 8, 50, 10, 15, 7, {"gold": 500}, 50, 1)

    # Create map
    game_map = GameMap(15, 15)
    for x in range(15):
        for y in range(15):
            tile = game_map.get_tile(x, y)
            if (x + y) % 7 == 0: tile.terrain_type = "forest"
            if (x * y) % 11 == 0: tile.terrain_type = "mountain"

    # Create POIs
    town1 = POI("town1", "town", (1, 1), 5, income={"gold": 200}, recruitable_units=[swordsman, archer, knight])
    mine1 = POI("mine1", "mine", (5, 5), 1, income={"gold": 50})
    mine2 = POI("mine2", "mine", (10, 5), 1, income={"gold": 50})
    fort1 = POI("fort1", "fort", (10, 10), 2, garrison=[Stack(swordsman, 10)])
    dungeon1 = POI("dungeon1", "dungeon", (7, 7), 3, garrison=[Stack(swordsman, 5), Stack(archer, 5)])

    game_map.set_poi(town1)
    game_map.set_poi(mine1)
    game_map.set_poi(mine2)
    game_map.set_poi(fort1)
    game_map.set_poi(dungeon1)

    # Create players
    p1 = Player(1, "Player 1")
    player_char = Character("Valeria", "Fighter", Stats(16, 12, 14, 10, 10, 10), max_hp=30, current_hp=30)
    h1 = Hero("Party 1", 1, position=(0, 0), party=[player_char])
    p1.heroes.append(h1)

    p2 = Player(2, "AI Opponent")
    ai_char = Character("Grok", "Orc", Stats(18, 10, 16, 8, 8, 8), max_hp=40, current_hp=40)
    h2 = Hero("Enemy Party", 2, position=(14, 14), party=[ai_char])
    p2.heroes.append(h2)

    return GameManager(game_map, [p1, p2])

def pixel_to_hex(px, py, size):
    # Adjust for offset in renderer
    width = math.sqrt(3) * size
    px -= width
    py -= size

    # Pointy top fractional axial coordinates
    q = (math.sqrt(3)/3 * px - 1/3 * py) / size
    r = (2/3 * py) / size

    # Round cube
    x, y, z = q, r, -q - r
    rx, ry, rz = round(x), round(y), round(z)
    dx, dy, dz = abs(rx - x), abs(ry - y), abs(rz - z)
    if dx > dy and dx > dz: rx = -ry - rz
    elif dy > dz: ry = -rx - rz
    else: rz = -rx - ry

    # Convert cube to pointy-top odd-r offset
    col = int(rx + (ry - (ry & 1)) // 2)
    row = int(ry)
    return col, row

def main():
    manager = create_game()
    ai = BasicAI(manager)
    hex_size = 25
    renderer = Renderer(800, 600, hex_size)
    clock = pygame.time.Clock()

    print("GUI Started (Hex Map). Left click to move hero, Space to end turn.")

    while True:
        player = manager.current_player

        if player.player_id == 2: # AI's turn
            print("AI is thinking...")
            pygame.time.delay(500)
            ai.execute_turn(player)
            continue

        hero = player.heroes[0] if player.heroes else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hero:
                mx, my = event.pos
                tx, ty = pixel_to_hex(mx, my, hex_size)
                result = manager.move_hero(hero, (tx, ty))
                print(result["message"])
                if result.get("interaction"):
                    print(f"Interaction: {result['interaction']['type']}")
                    if result['interaction'].get('xp_gained'):
                        print(f"XP Gained: {result['interaction']['xp_gained']}")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    manager.next_turn()
                    print(f"End turn. It's now {manager.current_player.name}'s turn.")

        state = manager.get_render_state()
        renderer.render_map(state)
        clock.tick(30)

if __name__ == "__main__":
    main()
