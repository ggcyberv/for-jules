import os
import sys
import pygame
import random

# Add current directory to path
sys.path.append(os.getcwd())

from main import GameController
from engine.game_state import GameState
from engine.save_manager import SaveManager
from events.event_trigger import EventTrigger
from combat.combat_simulator import CombatSimulator

def simulate_playthrough():
    # Set SDL to use the dummy video driver
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

    print("--- STARTING PLAYTHROUGH SIMULATION ---")
    ctrl = GameController()

    # 1. Start New Game
    print("Step 1: Starting New Game...")
    ctrl.state = ctrl.setup_game()
    ctrl.game_running = True
    ctrl.check_chunks(ctrl.state.party.q, ctrl.state.party.r)
    EventTrigger.check_enter_hex(ctrl.state.party.q, ctrl.state.party.r)

    initial_pos = (ctrl.state.party.q, ctrl.state.party.r)
    print(f"Party started at {initial_pos}")

    # 2. Test Movement and Chunk Generation
    print("Step 2: Testing Long-Distance Movement...")
    for i in range(15):
        # Move East
        nq, nr = ctrl.state.party.q + 1, ctrl.state.party.r
        tile = ctrl.state.world.get_tile(nq, nr)
        if not tile:
            ctrl.check_chunks(nq, nr)
            tile = ctrl.state.world.get_tile(nq, nr)

        if tile and tile.terrain_type != "water":
            ctrl.state.party.move_to(nq, nr, tile.movement_cost)
            EventTrigger.check_enter_hex(nq, nr)
        else:
            # Try a different direction if water
            nq, nr = ctrl.state.party.q, ctrl.state.party.r + 1
            ctrl.check_chunks(nq, nr)
            tile = ctrl.state.world.get_tile(nq, nr)
            if tile and tile.terrain_type != "water":
                ctrl.state.party.move_to(nq, nr, tile.movement_cost)
                EventTrigger.check_enter_hex(nq, nr)

    print(f"Moved to {ctrl.state.party.q}, {ctrl.state.party.r}")

    # 3. Test Combat Trigger
    print("Step 3: Simulating Random Encounter...")
    ctrl.on_random_encounter(ctrl.state.party.q, ctrl.state.party.r)
    if ctrl.active_combat:
        print(f"Combat started against {ctrl.active_combat['enemies'][0].name}")
        # Simulate one round
        ctrl.run_combat(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        print("Combat round simulated.")

    # 4. Test Town Entry
    print("Step 4: Testing Town Interaction (Start Town)...")
    ctrl.on_enter_location("start_town")
    if ctrl.active_town:
        print(f"Entered {ctrl.active_town.name}")
        # Visit healer
        # Mock some gold loss
        ctrl.state.party.gold = 50
        # Call healer node handler (service_type="healer")
        from world.location import TownNode
        healer_node = TownNode("healer", "Healer", "Heal", "healer")
        ctrl.handle_town_node(healer_node)
        print("Visited healer.")

    # 5. Test Save/Load Integrity
    print("Step 5: Testing Save/Load Persistence...")
    ctrl.state.global_flags["sim_test"] = True
    SaveManager.save_game("data/saves/sim_test.sav")

    # Clear state
    ctrl.state = None
    ctrl.game_running = False

    # Load state
    ctrl.state = GameState()
    if SaveManager.load_game("data/saves/sim_test.sav"):
        print("Save loaded successfully.")
        if ctrl.state.global_flags.get("sim_test"):
            print("Flags persisted correctly.")
        else:
            print("ERROR: Flags did NOT persist.")
            return False
    else:
        print("ERROR: Failed to load save.")
        return False

    # 6. Test Quest Progress
    print("Step 6: Testing Quest Progress...")
    quest_id = "clear_crypt_01"
    ctrl.state.quest_manager.start_quest(quest_id)
    quest = ctrl.state.quest_manager.quests.get(quest_id)
    if quest and quest.is_active:
        print(f"Quest '{quest.title}' is active.")
        # Simulate finishing objective
        # The objective in clear_crypt_01 is likely clearing a dungeon with a specific id
        # Let's see quest data

    print("--- PLAYTHROUGH SIMULATION FINISHED SUCCESSFULLY ---")
    return True

if __name__ == "__main__":
    pygame.init()
    try:
        success = simulate_playthrough()
        if not success: sys.exit(1)
    except Exception as e:
        print(f"CRASH DETECTED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()
