import pygame
import sys
from engine.models import Player, Hero, POI, Stack, UnitType
from engine.map import GameMap
from engine.manager import GameManager
from engine.graphics import Renderer

def create_game():
    # Define unit types
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    archer = UnitType("Archer", 6, 3, 15, 2, 6, 6, {"gold": 120}, 12, 1)

    # Create map
    game_map = GameMap(15, 15)
    # Add some terrain
    for x in range(15):
        for y in range(15):
            tile = game_map.get_tile(x, y)
            if (x + y) % 7 == 0: tile.terrain_type = "forest"
            if (x * y) % 11 == 0: tile.terrain_type = "mountain"

    # Create POIs
    town1 = POI("town1", "town", (1, 1), 5, income={"gold": 200}, recruitable_units=[swordsman, archer])
    mine1 = POI("mine1", "mine", (5, 5), 1, income={"gold": 50})
    fort1 = POI("fort1", "fort", (10, 10), 2, garrison=[Stack(swordsman, 10)])

    game_map.set_poi(town1)
    game_map.set_poi(mine1)
    game_map.set_poi(fort1)

    # Create players
    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(0, 0), army=[Stack(swordsman, 20), Stack(archer, 10)])
    p1.heroes.append(h1)

    p2 = Player(2, "AI Opponent")
    h2 = Hero("Hero 2", 2, position=(14, 14), army=[Stack(swordsman, 15)])
    p2.heroes.append(h2)

    return GameManager(game_map, [p1, p2])

def main():
    manager = create_game()
    renderer = Renderer(600, 600, 40)
    clock = pygame.time.Clock()

    print("GUI Started. Use arrow keys to move, Space to end turn, R to recruit, S to station.")

    while True:
        player = manager.current_player
        hero = player.heroes[0] if player.heroes else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and hero:
                target_pos = list(hero.position)
                moved = False

                if event.key == pygame.K_UP: target_pos[1] -= 1; moved = True
                elif event.key == pygame.K_DOWN: target_pos[1] += 1; moved = True
                elif event.key == pygame.K_LEFT: target_pos[0] -= 1; moved = True
                elif event.key == pygame.K_RIGHT: target_pos[0] += 1; moved = True
                elif event.key == pygame.K_SPACE:
                    manager.next_turn()
                    print(f"End turn. It's now {manager.current_player.name}'s turn.")

                if moved:
                    result = manager.move_hero(hero, tuple(target_pos))
                    print(result["message"])
                    if result.get("interaction"):
                        print(f"Interaction: {result['interaction']['type']}")

        state = manager.get_render_state()
        renderer.render_map(state)
        clock.tick(30)

if __name__ == "__main__":
    main()
