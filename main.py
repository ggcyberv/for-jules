import pygame
import sys
import secrets
import os
import random
from typing import Optional, List, Tuple
from engine.game_state import GameState
from engine.rng_manager import RNGManager
from engine.event_bus import event_bus
from world.world_generator import WorldGenerator
from world.dungeon_generator import DungeonGenerator
from world.hex_grid import HexGrid
from party.party_manager import Party
from party.character import Character
from party.item import Item, Weapon, Armor
from ui.overworld_view import OverworldView
from ui.event_view import EventView
from ui.dungeon_view import DungeonView
from ui.town_view import TownView
from ui.party_view import PartyView
from ui.combat_view import CombatView
from events.event_trigger import EventTrigger
from events.event_template import EventManager, EventTemplate, EventChoice
from events.consequence_engine import ConsequenceEngine
from combat.combat_simulator import CombatSimulator
from combat.tactics import TacticType, FormationType, AIPriority
from world.location import Town, Dungeon, TownNode
from engine.save_manager import SaveManager
from engine.audio_manager import AudioManager

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Chronicles of the Unbound Realm")

        self.audio = AudioManager()
        self.world_gen = None
        self.state = self.setup_game()

        self.overworld_view = OverworldView(800, 600)
        self.event_view = EventView(800, 600)
        self.dungeon_view = DungeonView(800, 600)
        self.town_view = TownView(800, 600)
        self.party_view = PartyView(800, 600)
        self.combat_view = CombatView(800, 600)

        self.event_manager = EventManager()
        self.event_manager.load_templates("data/events")
        self.event_manager.load_quests("data/quests", self.state.quest_manager)
        self.clock = pygame.time.Clock()
        self.logs = ["Welcome to the Unbound Realm."]
        self.active_event: Optional[EventTemplate] = None
        self.active_town: Optional[Town] = None
        self.show_party_screen = False

        # Combat State
        self.active_combat = None
        self.combat_log = []
        self.current_tactic = TacticType.BALANCED
        self.current_formation = FormationType.NONE
        self.current_priority = AIPriority.NEAREST

        event_bus.subscribe("hex_discovered", self.on_hex_discovered)
        event_bus.subscribe("random_encounter", self.on_random_encounter)
        event_bus.subscribe("enter_location", self.on_enter_location)
        event_bus.subscribe("trigger_story_event", self.on_trigger_story_event)
        event_bus.subscribe("request_generation", self.check_chunks)

        # Ensure starting area is fully loaded and discovered
        self.check_chunks(0, 0)
        EventTrigger.check_enter_hex(0, 0)

    def setup_game(self):
        seed = secrets.randbits(32)
        settings = {"danger_level": 0.6}
        self.world_gen = WorldGenerator(seed, settings)
        grid = HexGrid(chunk_size=10)

        hero1 = Character("Alaric", attack=15, defense=10, speed=6, accuracy=85, critical_chance=10, backstory="A disgraced knight seeking redemption.")
        hero2 = Character("Elara", attack=10, defense=12, speed=5, accuracy=90, critical_chance=5, backstory="A nomadic healer from the eastern plains.")
        party = Party(members=[hero1, hero2])

        state = GameState()
        state.initialize(grid, party, seed, self.world_gen.locations)
        return state

    def check_chunks(self, q, r):
        # Proactively generate chunks in a larger area
        for dq in range(-2, 3):
            for dr in range(-2, 3):
                target_q = q + dq * 10
                target_r = r + dr * 10
                cq, cr = self.state.world.get_chunk_coords(target_q, target_r)
                self.world_gen.generate_chunk(self.state.world, cq, cr)

    def on_hex_discovered(self, q, r):
        self.logs.append(f"Discovered hex at ({q}, {r})")

    def on_random_encounter(self, q, r):
        enemy_id = "orc" if random.random() < 0.5 else "skeleton"
        enemy = CombatSimulator.load_enemy(enemy_id)
        self.logs.append(f"Encounter! A {enemy.name} blocks your path.")
        self.active_combat = {"enemies": [enemy], "turn": 1}
        self.combat_log = [f"Battle against {enemy.name} initiated!"]

    def on_enter_location(self, poi_id):
        loc = self.state.locations.get(poi_id)
        if isinstance(loc, Town):
            self.active_town = loc
            self.logs.append(f"Entered town: {loc.name}.")
        elif isinstance(loc, Dungeon):
            self.logs.append(f"Entering dungeon: {loc.name}!")
            gen = DungeonGenerator(self.state.seed + loc.q + loc.r)
            self.state.active_dungeon = gen.generate(40, 20)
            self.state.active_dungeon_id = poi_id
            self.state.dungeon_pos = self.state.active_dungeon.start_pos
            self.state.compute_fov()

    def on_trigger_story_event(self, event_id, title=None, desc=None, choices=None):
        if choices:
            event = EventTemplate(event_id, title, desc, [EventChoice(c["text"], c["outcome"]) for c in choices])
        else:
            event = self.event_manager.get_event(event_id)
        if event and event.check_conditions(self.state):
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
                else: self.logs.append("Party is full!")
            else: self.logs.append("Not enough gold!")
        elif outcome["type"] == "buy":
            if self.state.party.gold >= outcome["cost"]:
                self.state.party.gold -= outcome["cost"]
                self.state.party.inventory.append(outcome["item"])
                outcome["loc"].inventory.remove(outcome["item"])
                self.logs.append(f"Purchased {outcome['item'].name}!")
            else: self.logs.append("Not enough gold!")
        self.active_event = None

    def run_overworld(self, event):
        self.audio.play_ambient("overworld")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            tq, tr = self.overworld_view.pixel_to_hex(mx, my)

            # Ensure the chunk we clicked is generated
            self.check_chunks(tq, tr)

            dist = self.state.world.distance(self.state.party.q, self.state.party.r, tq, tr)
            if dist == 1:
                tile = self.state.world.get_tile(tq, tr)
                if tile and tile.terrain_type != "water":
                    last_q, last_r = self.state.party.q, self.state.party.r
                    if self.state.party.move_to(tq, tr, tile.movement_cost):
                        # Reveal surroundings on move
                        EventTrigger.check_enter_hex(tq, tr, last_q, last_r)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.state.advance_turn()
                EventTrigger.check_wait()
                EventTrigger.check_time()
                self.logs.append(f"Turn {self.state.turn} begins.")
                if self.state.ironman:
                    SaveManager.save_game("data/saves/ironman.sav")
            elif event.key == pygame.K_s:
                SaveManager.save_game("data/saves/quicksave.sav")
                self.logs.append("Game saved.")
            elif event.key == pygame.K_l:
                if SaveManager.load_game("data/saves/quicksave.sav"): self.logs.append("Game loaded.")
                else: self.logs.append("Failed to load save.")
            elif event.key == pygame.K_t:
                tl = list(TacticType)
                self.current_tactic = tl[(tl.index(self.current_tactic) + 1) % len(tl)]
                self.logs.append(f"Tactic: {self.current_tactic.value}")
            elif event.key == pygame.K_i:
                self.show_party_screen = True

    def run_dungeon(self, event):
        self.audio.play_ambient("dungeon")
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

                    if tile.trap_id:
                        self.logs.append(f"TRAP! You triggered a {tile.trap_id}!")
                        for m in self.state.party.members:
                            m.hp -= 10
                        tile.trap_id = None # One-time trigger

                    if (nx, ny) == self.state.active_dungeon.exit_pos:
                        quest = self.state.quest_manager.update_objective(f"dungeon_cleared_{self.state.active_dungeon_id}")
                        if quest:
                            self.logs.append(f"QUEST COMPLETE: {quest.title}!")
                            self.state.party.gold += quest.rewards.get("gold", 0)
                        self.logs.append("Dungeon cleared!")
                        self.state.active_dungeon = None

    def run_town(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self.town_view.handle_click(event.pos)
            if idx is not None: self.handle_town_node(self.active_town.nodes[idx])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active_town = None
                self.logs.append("Left town.")

    def run_combat(self, event):
        self.audio.play_ambient("combat")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.combat_view.handle_click(event.pos)
            if action:
                if action == "retreat":
                    self.logs.append("Party retreated from battle!")
                    self.active_combat = None
                else:
                    int_log = CombatSimulator.resolve_intervention(action, self.state.party.members, self.active_combat["enemies"])
                    self.combat_log.extend(int_log)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                res = CombatSimulator.simulate_round(self.state.party.members, self.active_combat["enemies"], self.active_combat["turn"], self.current_tactic, self.current_formation, self.current_priority)
                self.combat_log.extend(res["log"])

                # Add visual effects for hits
                for line in res["log"]:
                    if "attacks" in line:
                        target_name = line.split("attacks ")[1].split(" for")[0]
                        fx_pos = (700, 100) # Default enemy area
                        if "Enemy" in line: fx_pos = (100, 100) # Party area

                        # Find actual position
                        if "Enemy" in line:
                            for idx, m in enumerate(self.state.party.members):
                                if m.name in target_name: fx_pos = (100, 100 + idx * 80); break
                        else:
                            for idx, e in enumerate(self.active_combat["enemies"]):
                                if e.name in target_name: fx_pos = (700, 100 + idx * 80); break

                        fx_type = "slash" if "attacks" in line else "spark"
                        self.combat_view.effects.append((fx_type, fx_pos, 5))

                self.active_combat["turn"] += 1

                # Check outcome
                if not any(e.hp > 0 for e in self.active_combat["enemies"]):
                    xp = len(self.active_combat["enemies"]) * 20
                    # Success builds bonds
                    for m1 in self.state.party.members:
                        if m1.hp > 0:
                            m1.gain_xp(xp)
                            for m2 in self.state.party.members:
                                if m1 != m2 and m2.hp > 0:
                                    m1.adjust_relationship(m2.name, 2)
                    self.logs.append(f"Combat Victory! Gained {xp} XP.")
                    self.active_combat = None
                elif not any(m.hp > 0 for m in self.state.party.members):
                    self.logs.append("Party Wiped Out...")
                    self.active_combat = None

    def handle_town_node(self, node: TownNode):
        if node.service_type == "healer":
            cost = self.active_town.healing_cost
            if self.state.party.gold >= cost:
                self.state.party.gold -= cost
                for m in self.state.party.members: m.hp = m.max_hp
                self.logs.append("Party healed.")
            else: self.logs.append("Not enough gold.")
        elif node.service_type == "recruit":
            if self.active_town.recruits:
                r = self.active_town.recruits[0]
                self.on_trigger_story_event("recruit_offer_" + self.active_town.poi_id, title=f"New Recruit: {r.name}", desc=f"{r.name} wants to join for {self.active_town.recruitment_cost} gold.", choices=[{"text": f"Recruit {r.name}", "outcome": {"type": "recruit", "recruit": r, "cost": self.active_town.recruitment_cost, "loc": self.active_town}}, {"text": "Maybe later", "outcome": {"type": "message", "text": "Declined."}}])
            else: self.logs.append("No recruits.")
        elif node.service_type == "market":
            if self.active_town.inventory:
                item = self.active_town.inventory[0]
                self.on_trigger_story_event("market_buy_" + self.active_town.poi_id, title="Market", desc=f"Buy {item.name} for {item.value} gold?", choices=[{"text": f"Buy {item.name}", "outcome": {"type": "buy", "item": item, "cost": item.value, "loc": self.active_town}}, {"text": "Leave", "outcome": {"type": "message", "text": "Browsing finished."}}])
            else: self.logs.append("Market is empty.")
        elif node.service_type == "guild":
            available_quests = [q for q in self.state.quest_manager.quests.values() if not q.is_active and not q.is_finished]
            if available_quests:
                quest = available_quests[0]
                self.on_trigger_story_event("quest_offer_" + quest.quest_id, title=f"Quest: {quest.title}", desc=f"{quest.description}", choices=[{"text": "Accept Quest", "outcome": {"type": "message", "text": f"Accepted {quest.title}!", "start_quest": quest.quest_id}}, {"text": "Decline", "outcome": {"type": "message", "text": "Maybe another time."}}])
            else:
                self.logs.append("The quest board is currently empty.")
        else:
            self.logs.append(f"Visited {node.name}. (Service not implemented)")

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if self.active_event:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        idx = self.event_view.handle_click(event.pos)
                        if idx is not None: self.resolve_choice(idx)
                    continue
                if self.active_combat: self.run_combat(event); continue
                if self.show_party_screen:
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_i, pygame.K_ESCAPE]: self.show_party_screen = False
                        else: self.party_view.handle_keydown(event.key)
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.party_view.handle_click(event.pos, self.state.party): self.logs.append("Attribute increased!")
                    continue
                if self.active_town: self.run_town(event)
                elif self.state.active_dungeon: self.run_dungeon(event)
                else: self.run_overworld(event)
            if self.active_combat: self.combat_view.render(self.screen, self.state.party.members, self.active_combat["enemies"], self.combat_log, self.active_combat["turn"])
            elif self.show_party_screen: self.party_view.render(self.screen, self.state.party)
            elif self.active_town: self.town_view.render(self.screen, self.active_town)
            elif self.state.active_dungeon: self.dungeon_view.render(self.screen, self.state.active_dungeon, self.state.dungeon_pos)
            else: self.overworld_view.render(self.screen, self.state.world, (self.state.party.q, self.state.party.r), self.logs)
            if self.active_event: self.event_view.render(self.screen, self.active_event)
            pygame.display.flip(); self.clock.tick(30)

if __name__ == "__main__":
    controller = GameController()
    controller.run()
