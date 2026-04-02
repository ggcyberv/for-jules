import os
# Set SDL to use the dummy video driver for headless environments
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from engine.game_state import GameState
from world.world_generator import WorldGenerator
from party.party_manager import Party
from party.character import Character
from ui.overworld_view import OverworldView

def verify_visuals():
    pygame.init()
    # Even with dummy driver, we can create a surface
    screen = pygame.Surface((800, 600))

    seed = 12345
    settings = {"world_size": (15, 10), "danger_level": 0.6}
    world_gen = WorldGenerator(seed, settings)
    grid = world_gen.generate()

    hero1 = Character("Alaric")
    party = Party(members=[hero1])
    state = GameState()
    state.initialize(grid, party, seed, world_gen.locations)
    grid.get_tile(0, 0).discovered = True

    view = OverworldView(800, 600)
    view.render(screen, grid, (0, 0), ["Game Initialized", "Welcome to Riverfall"])

    output_dir = "verification/screenshots"
    os.makedirs(output_dir, exist_ok=True)
    pygame.image.save(screen, os.path.join(output_dir, "verification.png"))
    print(f"Screenshot saved to {output_dir}/verification.png")
    pygame.quit()

if __name__ == "__main__":
    verify_visuals()
