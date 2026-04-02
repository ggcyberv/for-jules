import pygame
import sys
import secrets
import os
from typing import Optional, List, Tuple
from engine.game_state import GameState
from engine.rng_manager import RNGManager
from engine.event_bus import event_bus
from world.world_generator import WorldGenerator
from world.dungeon_generator import DungeonGenerator
from party.party_manager import Party
from party.character import Character
from ui.overworld_view import OverworldView
from ui.event_view import EventView
from ui.dungeon_view import DungeonView
from ui.town_view import TownView
from events.event_trigger import EventTrigger
from events.event_template import EventManager, EventTemplate, EventChoice
from events.consequence_engine import ConsequenceEngine
from combat.combat_simulator import CombatSimulator
from combat.tactics import TacticType
from world.location import Town, Dungeon, TownNode
from engine.save_manager import SaveManager

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Chronicles of the Unbound Realm")
        self.state = self.setup_game()
        self.overworld_view = OverworldView(800, 600)
        self.event_view = EventView(800, 600)
        self.dungeon_view = DungeonView(800, 600)
        self.town_view = TownView(800, 600)
        self.event_manager = EventManager()
        self.event_manager.load_templates("data/events")
        self.clock = pygame.time.Clock()
        self.logs = ["Welcome to the Unbound Realm."]
        self.active_event: Optional[EventTemplate] = None
        self.active_town: Optional[Town] = None
        self.current_tactic = TacticType.BALANCED

        # Subscribe to events
        event_bus.subscribe("hex_discovered", self.on_hex_discovered)
        event_bus.subscribe("random_encounter", self.on_random_encounter)
        event_bus.subscribe("enter_location", self.on_enter_location)
        event_bus.subscribe("trigger_story_event", self.on_trigger_story_event)

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

        # Register a starting faction
        from world.faction_system import Faction
        state.faction_system.register_faction(Faction("citizens", "Riverfall Citizens", "Local townsfolk."))

        return state

    def on_hex_discovered(self, q, r):
        self.logs.append(f"Discovered hex at ({q}, {r})")

    def on_random_encounter(self, q, r):
        self.logs.append(f"Encounter! (Tactic: {self.current_tactic.value})")
        enemies = [Character("Goblin", hp=30, attack=8, defense=5, speed=4)]
        result = CombatSimulator.simulate_battle(self.state.party.members, enemies, self.current_tactic)
        if result["victory"]:
            self.logs.append("Victory! Gained XP.")
        else:
            self.logs.append("Defeat... The party is wounded.")

    def on_enter_location(self, poi_id):
        loc = self.state.locations.get(poi_id)
        if isinstance(loc, Town):
            self.active_town = loc
            self.logs.append(f"Entered town: {loc.name}.")
        elif isinstance(loc, Dungeon):
            self.logs.append(f"Entering dungeon: {loc.name}!")
            gen = DungeonGenerator(self.state.seed + loc.q + loc.r)
            self.state.active_dungeon = gen.generate(40, 20)
            self.state.dungeon_pos = self.state.active_dungeon.start_pos
            self.state.compute_fov()

    def on_trigger_story_event(self, event_id, title=None, desc=None, choices=None):
        if choices:
            event = EventTemplate(event_id, title, desc, [EventChoice(c["text"], c["outcome"]) for c in choices])
        else:
            event = self.event_manager.get_event(event_id)

        if event:
            self.active_event = event

    def resolve_choice(self, choice_idx):
        choice = self.active_event.choices[choice_idx]
        outcome = choice.outcome
        ConsequenceEngine.apply_consequence(outcome)

        if outcome["type"] == "encounter":
            self.on_random_encounter(0, 0)
        elif outcome["type"] == "message":
            self.logs.append(outcome["text"])
        elif outcome["type"] == "recruit":
            if self.state.party.gold >= outcome["cost"]:
                if self.state.party.add_member(outcome["recruit"]):
                    self.state.party.gold -= outcome["cost"]
                    outcome["loc"].recruits.remove(outcome["recruit"])
                    self.logs.append(f"{outcome['recruit'].name} joined the party!")
                else:
                    self.logs.append("Party is full!")
            else:
                self.logs.append("Not enough gold!")

        self.active_event = None

    def run_overworld(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            tq, tr = self.overworld_view.pixel_to_hex(mx, my)
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
            elif event.key == pygame.K_s:
                SaveManager.save_game("data/saves/quicksave.sav")
                self.logs.append("Game saved.")
            elif event.key == pygame.K_l:
                if SaveManager.load_game("data/saves/quicksave.sav"):
                    self.logs.append("Game loaded.")
                else:
                    self.logs.append("Failed to load save.")
            elif event.key == pygame.K_t:
                tactics_list = list(TacticType)
                idx = (tactics_list.index(self.current_tactic) + 1) % len(tactics_list)
                self.current_tactic = tactics_list[idx]
                self.logs.append(f"Current Tactic: {self.current_tactic.value}")

    def run_dungeon(self, event):
        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP: dy = -1
            elif event.key == pygame.K_DOWN: dy = 1
            elif event.key == pygame.K_LEFT: dx = -1
            elif event.key == pygame.K_RIGHT: dx = 1
            elif event.key == pygame.K_ESCAPE:
                self.state.active_dungeon = None
                self.logs.append("Returned to Overworld.")
                return

            if dx != 0 or dy != 0:
                nx, ny = self.state.dungeon_pos[0] + dx, self.state.dungeon_pos[1] + dy
                tile = self.state.active_dungeon.get_tile(nx, ny)
                if tile and not tile.is_wall:
                    self.state.dungeon_pos = (nx, ny)
                    self.state.compute_fov()
                    if (nx, ny) == self.state.active_dungeon.exit_pos:
                        self.logs.append("Dungeon cleared!")
                        self.state.active_dungeon = None

    def run_town(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self.town_view.handle_click(event.pos)
            if idx is not None:
                node = self.active_town.nodes[idx]
                self.handle_town_node(node)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active_town = None
                self.logs.append("Left town.")

    def handle_town_node(self, node: TownNode):
        if node.service_type == "healer":
            cost = self.active_town.healing_cost
            if self.state.party.gold >= cost:
                self.state.party.gold -= cost
                for m in self.state.party.members: m.hp = m.max_hp
                self.logs.append("Party healed at the temple.")
            else:
                self.logs.append("Not enough gold for healing.")
        elif node.service_type == "recruit":
            if self.active_town.recruits:
                recruit = self.active_town.recruits[0]
                self.on_trigger_story_event("recruit_offer_" + self.active_town.poi_id,
                                          title=f"New Recruit: {recruit.name}",
                                          desc=f"A brave soul named {recruit.name} wants to join your party for {self.active_town.recruitment_cost} gold.",
                                          choices=[
                                              {"text": f"Recruit {recruit.name}", "outcome": {"type": "recruit", "recruit": recruit, "cost": self.active_town.recruitment_cost, "loc": self.active_town}},
                                              {"text": "Maybe later", "outcome": {"type": "message", "text": "You declined the offer."}}
                                          ])
            else:
                self.logs.append("No recruits available.")
        else:
            self.logs.append(f"Visited {node.name}. (Service not implemented)")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.active_event:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        choice_idx = self.event_view.handle_click(event.pos)
                        if choice_idx is not None:
                            self.resolve_choice(choice_idx)
                    continue

                if self.active_town:
                    self.run_town(event)
                elif self.state.active_dungeon:
                    self.run_dungeon(event)
                else:
                    self.run_overworld(event)

            if self.active_town:
                self.town_view.render(self.screen, self.active_town)
            elif self.state.active_dungeon:
                self.dungeon_view.render(self.screen, self.state.active_dungeon, self.state.dungeon_pos)
            else:
                self.overworld_view.render(self.screen, self.state.world, (self.state.party.q, self.state.party.r), self.logs)

            if self.active_event:
                self.event_view.render(self.screen, self.active_event)
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    controller = GameController()
    controller.run()
