import os
# Set SDL to use the dummy video driver for headless environments
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from engine.game_state import GameState
from world.world_generator import WorldGenerator
from party.party_manager import Party
from party.character import Character
from world.faction_system import Faction
from ui.overworld_view import OverworldView

def verify_visuals():
    pygame.init()
    # Even with dummy driver, we can create a surface
    screen = pygame.display.set_mode((800, 600))

    seed = 12345
    settings = {"world_size": (15, 10), "danger_level": 0.6}
    world_gen = WorldGenerator(seed, settings)
    from world.hex_grid import HexGrid
    grid = HexGrid(chunk_size=10)
    world_gen.generate_chunk(grid, 0, 0)

    hero1 = Character("Alaric", level=2, hp=90, max_hp=110)
    hero2 = Character("Elara", level=1, hp=100, max_hp=100)
    party = Party(members=[hero1, hero2])
    state = GameState()
    state.initialize(grid, party, seed, world_gen.locations)
    grid.get_tile(0, 0).discovered = True

    # Setup faction
    state.faction_system.register_faction(Faction("citizens", "Riverfall Citizens", "Local townsfolk.", starting_reputation=10))

    view = OverworldView(800, 600)
    view.render(screen, grid, (0, 0), ["Game Initialized", "Welcome to Riverfall", "Faction reputation: Neutral"])

    output_dir = "verification/screenshots"
    os.makedirs(output_dir, exist_ok=True)
    pygame.image.save(screen, os.path.join(output_dir, "verification_overworld.png"))

    # Verify Combat UI
    from ui.combat_view import CombatView
    combat_view = CombatView(800, 600)
    enemy = Character("Orc", hp=50)
    combat_view.effects.append(("slash", (680, 100), 5))
    combat_view.render(screen, party.members, [enemy], ["Battle started!", "Alaric attacks Orc for 10 damage!"], 1)
    pygame.image.save(screen, os.path.join(output_dir, "verification_combat.png"))

    # Verify Party UI
    from ui.party_view import PartyView
    party_view = PartyView(800, 600)
    party_view.render(screen, party)
    pygame.image.save(screen, os.path.join(output_dir, "verification_party.png"))

    # Verify Town UI
    from ui.town_view import TownView
    from world.location import Town, TownNode
    town_view = TownView(800, 600)
    town = Town("test_town", "Veridia", 0, 0)
    town.nodes = [TownNode("market", "Market", "Buy goods.", "market"), TownNode("healer", "Healer", "Heal wounds.", "healer")]
    town_view.render(screen, town)
    pygame.image.save(screen, os.path.join(output_dir, "verification_town.png"))

    # Verify Event UI
    from ui.event_view import EventView
    from events.event_template import EventTemplate, EventChoice
    event_view = EventView(800, 600)
    event = EventTemplate("test_event", "Mysterious Stranger", "A man in a hooded cloak approaches your camp.", [EventChoice("Listen", {"type": "message", "text": "He tells a tale."}), EventChoice("Ignore", {"type": "message", "text": "He vanishes."})])
    event_view.render(screen, event)
    pygame.image.save(screen, os.path.join(output_dir, "verification_event.png"))

    os.makedirs(output_dir, exist_ok=True)
    pygame.image.save(screen, os.path.join(output_dir, "verification.png"))
    print(f"Screenshot saved to {output_dir}/verification.png")
    pygame.quit()

if __name__ == "__main__":
    verify_visuals()
