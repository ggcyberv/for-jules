import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import sys
from main import GameController
from world.location import Town

def test():
    pygame.init()
    gc = GameController()
    gc.state = gc.setup_game()
    gc.game_running = True

    # Enter town
    town = gc.state.locations.get("start_town")
    if not town:
        # Manually create it if world gen didn't pick that exact ID
        from world.location import Town
        town = Town("start_town", "Riverfall", 0, 0)
    gc.active_town = town

    # Simulate ESC key
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0, "unicode": ""})

    print("Testing ESC in town...")
    try:
        gc.run_town(event)
        print(f"run_town finished. active_town is now: {gc.active_town}")

        # Simulate rendering part of the main loop
        gc.screen.fill((0, 0, 0))
        if gc.active_town:
            gc.town_view.render(gc.screen, gc.active_town)
        elif gc.state and gc.state.active_dungeon:
            gc.dungeon_view.render(gc.screen, gc.state.active_dungeon, gc.state.dungeon_pos)
        elif gc.state:
            gc.overworld_view.render(gc.screen, gc.state.world, (gc.state.party.q, gc.state.party.r), gc.logs)
        print("Rendering finished.")
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
