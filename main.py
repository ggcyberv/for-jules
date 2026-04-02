import pygame
import sys
import secrets
from engine.game_state import GameState
from engine.rng_manager import RNGManager
from engine.event_bus import event_bus
from world.world_generator import WorldGenerator
from party.party_manager import Party
from party.character import Character
from ui.overworld_view import OverworldView
from events.event_trigger import EventTrigger
from combat.combat_simulator import CombatSimulator
from world.location import Town, Dungeon

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Chronicles of the Unbound Realm")
        self.state = self.setup_game()
        self.view = OverworldView(800, 600)
        self.clock = pygame.time.Clock()
        self.logs = ["Welcome to the Unbound Realm."]

        # Subscribe to events
        event_bus.subscribe("hex_discovered", self.on_hex_discovered)
        event_bus.subscribe("random_encounter", self.on_random_encounter)
        event_bus.subscribe("enter_location", self.on_enter_location)

    def setup_game(self):
        seed = secrets.randbits(32)
        settings = {"world_size": (15, 10), "danger_level": 0.6}
        world_gen = WorldGenerator(seed, settings)
        grid = world_gen.generate()

        hero1 = Character("Alaric", attack=15, defense=10, speed=6)
        hero2 = Character("Elara", attack=10, defense=12, speed=5)
        party = Party(members=[hero1, hero2])

        state = GameState()
        state.initialize(grid, party, seed, world_gen.locations)
        grid.get_tile(0, 0).discovered = True
        return state

    def on_hex_discovered(self, q, r):
        self.logs.append(f"Discovered hex at ({q}, {r})")

    def on_random_encounter(self, q, r):
        self.logs.append("Dangerous encounter!")
        enemies = [Character("Goblin", hp=30, attack=8, defense=5, speed=4)]
        result = CombatSimulator.simulate_battle(self.state.party.members, enemies)
        if result["victory"]:
            self.logs.append("Victory! Gained XP.")
        else:
            self.logs.append("Defeat... The party is wounded.")

    def on_enter_location(self, poi_id):
        loc = self.state.locations.get(poi_id)
        if isinstance(loc, Town):
            self.logs.append(f"Entered town: {loc.name}. Party rested.")
            self.state.party.gold += 10 # Sample town interaction
            self.state.party.rest()
        elif isinstance(loc, Dungeon):
            self.logs.append(f"Entering dungeon: {loc.name}!")
            enemies = [Character("Skeleton", hp=40, attack=10, defense=8, speed=3)]
            result = CombatSimulator.simulate_battle(self.state.party.members, enemies)
            if result["victory"]:
                self.logs.append("Dungeon cleared! Found treasure.")
                self.state.party.gold += 50
                loc.is_cleared = True
            else:
                self.logs.append("Fled the dungeon in defeat.")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    tq, tr = self.view.pixel_to_hex(mx, my)
                    dist = self.state.world.distance(self.state.party.q, self.state.party.r, tq, tr)
                    if dist == 1:
                        tile = self.state.world.get_tile(tq, tr)
                        if tile and tile.terrain_type != "water":
                            if self.state.party.move_to(tq, tr, int(tile.movement_cost)):
                                EventTrigger.check_enter_hex(tq, tr)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.state.advance_turn()
                        self.logs.append(f"Turn {self.state.turn} begins.")

            self.view.render(self.screen, self.state.world, (self.state.party.q, self.state.party.r), self.logs)
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    controller = GameController()
    controller.run()
