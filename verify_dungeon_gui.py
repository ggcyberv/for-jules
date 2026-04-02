import os
# Headless
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from engine.game_state import GameState
from world.world_generator import WorldGenerator
from world.dungeon_generator import DungeonGenerator
from party.party_manager import Party
from party.character import Character
from ui.dungeon_view import DungeonView

def verify_dungeon_visuals():
    pygame.init()
    screen = pygame.Surface((800, 600))

    gen = DungeonGenerator(123)
    dungeon = gen.generate(40, 20)

    state = GameState()
    state.active_dungeon = dungeon
    state.dungeon_pos = dungeon.start_pos
    state.compute_fov()

    view = DungeonView(800, 600)
    view.render(screen, dungeon, state.dungeon_pos)

    output_dir = "verification/screenshots"
    os.makedirs(output_dir, exist_ok=True)
    pygame.image.save(screen, os.path.join(output_dir, "dungeon_verification.png"))
    print(f"Dungeon Screenshot saved to {output_dir}/dungeon_verification.png")
    pygame.quit()

if __name__ == "__main__":
    verify_dungeon_visuals()
