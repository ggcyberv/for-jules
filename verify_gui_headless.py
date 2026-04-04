import pygame
import sys
import os
import time

# Set dummy video driver for headless screenshots
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from main import GameController

def capture_screenshot(controller, filename):
    # Manually trigger a few frames of rendering
    controller.screen.fill((0, 0, 0))

    # Simulate a "New Game" state rendering
    if not controller.game_running:
        controller.menu_view.render(controller.screen)
    elif controller.active_combat:
        controller.combat_view.render(controller.screen, controller.state.party.members, controller.active_combat["enemies"], controller.combat_log, controller.active_combat["turn"])
    elif controller.active_town:
        controller.town_view.render(controller.screen, controller.active_town)
    else:
        controller.overworld_view.render(controller.screen, controller.state.world, (controller.state.party.q, controller.state.party.r), controller.logs)

    if controller.message_view.active_message:
        controller.message_view.render(controller.screen)

    pygame.display.flip()
    pygame.image.save(controller.screen, f"/home/jules/verification/screenshots/{filename}")
    print(f"Captured {filename}")

def main():
    gc = GameController()

    # 1. Menu Screenshot
    capture_screenshot(gc, "01_menu.png")

    # 2. Start Game & Overworld
    gc.state = gc.setup_game()
    gc.game_running = True
    gc.check_chunks(0, 0)
    gc.state.compute_overworld_visibility()
    capture_screenshot(gc, "02_overworld.png")

    # 3. Combat Screenshot
    from combat.combat_simulator import CombatSimulator
    enemy = CombatSimulator.load_enemy("orc")
    gc.active_combat = {"enemies": [enemy], "turn": 1}
    gc.combat_log = ["Battle started!", "Alaric attacks Orc for 10 damage!"]
    capture_screenshot(gc, "03_combat.png")

    # 4. Town Screenshot
    from world.location import Town, TownNode
    town = Town("test_town", "Riverfall", 0, 0)
    town.nodes = [TownNode("healer", "Healer", "Restore health.", "healer")]
    gc.active_town = town
    gc.active_combat = None
    capture_screenshot(gc, "04_town.png")

if __name__ == "__main__":
    main()
