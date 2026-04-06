import pygame
import sys
import secrets
import os
import random
from typing import Optional, List, Tuple, Any
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
from ui.menu_view import MenuView
from ui.message_view import MessageView
from ui.pre_battle_view import PreBattleView
from ui.end_view import EndView
from ui.pause_view import PauseView

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Chronicles of the Unbound Realm")

        self.audio = AudioManager()
        self.world_gen = None
        self.world_settings = {
            "danger_level": 0.6,
            "urbanization": 0.4,
            "loot_abundance": 0.5,
            "magic_frequency": 0.6,
            "faction_hostility": 0.3
        }
        self.state = GameState()
        self.game_running = False

        self.menu_view = MenuView(800, 600)
        self.message_view = MessageView(800, 600)
        self.pre_battle_view = PreBattleView(800, 600)
        self.end_view = EndView(800, 600)
        self.pause_view = PauseView(800, 600)
        self.overworld_view = OverworldView(800, 600)
        self.event_view = EventView(800, 600)
        self.dungeon_view = DungeonView(800, 600)
        self.town_view = TownView(800, 600)
        self.party_view = PartyView(800, 600)
        self.combat_view = CombatView(800, 600)

        self.event_manager = EventManager()
        self.event_manager.load_templates("data/events")
        self.clock = pygame.time.Clock()
        self.logs = ["Welcome to the Unbound Realm."]
        self.active_event: Optional[EventTemplate] = None
        self.active_town: Optional[Town] = None
        self.show_party_screen = False

        self.transition_alpha = 0
        self.transition_target = None # "overworld", "combat", "town", etc.

        # Combat State
        self.active_combat = None
        self.pre_battle_active = False
        self.paused = False
        self.game_over = False
        self.victory = False
        self.combat_log = []
        self.combat_queue = []
        self.combat_timer = 0
        self.combat_paused = False
        self.combat_speed = 1.0 # 1.0 = normal, 2.0 = fast
        self.current_formation = FormationType.NONE

        event_bus.subscribe("hex_discovered", self.on_hex_discovered)
        event_bus.subscribe("random_encounter", self.on_random_encounter)
        event_bus.subscribe("enter_location", self.on_enter_location)
        event_bus.subscribe("trigger_story_event", self.on_trigger_story_event)
        event_bus.subscribe("request_generation", self.check_chunks)

    def setup_game(self, seed: Optional[Any] = None):
        if seed is None:
            seed = secrets.randbits(32)
        elif isinstance(seed, str):
            # Deterministic hash of string to int
            import hashlib
            seed = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (2**32)

        self.world_gen = WorldGenerator(seed, self.world_settings)

        from world.faction_system import NPCParty
        grid = HexGrid(chunk_size=10)

        hero1 = Character(
            "Alaric",
            backstory_name="Soldier",
            race="Human",
            base_str=12, base_con=12,
            backstory="A disgraced knight seeking redemption."
        )
        hero2 = Character(
            "Elara",
            backstory_name="Acolyte",
            race="Elf",
            age_category="Young",
            base_int=12, base_cha=12,
            backstory="A nomadic healer from the eastern plains."
        )
        party = Party(members=[hero1, hero2])

        state = GameState()
        state.initialize(grid, party, seed, self.world_gen.locations)
        self.event_manager.load_quests("data/quests", state.quest_manager)

        # Set initial faction relations based on hostility
        hostility = self.world_settings.get("faction_hostility", 0.3)
        for faction_id in ["bandits", "undead"]:
            state.faction_system.adjust_reputation(faction_id, -int(hostility * 100))

        # Manually initialize HP/Mana
        for m in party.members:
            m.hp = m.max_hp
            m.mana = m.max_mana

        # Initial Global Diplomacy
        state.faction_system.adjust_faction_relation("nomads", "bandits", -30)

        # Spawn some NPC parties
        state.npc_parties.append(NPCParty("bandit_patrol_1", "bandits", "Bandit Raiders", 5, 5, [CombatSimulator.load_enemy("bandit")], behavior="chase"))
        state.npc_parties.append(NPCParty("citizen_patrol_1", "citizens", "Town Guards", 0, 0, [CombatSimulator.load_enemy("skeleton")], behavior="patrol", patrol_origin=(0,0)))

        # Test Encounter: A wolf pack blocking the way near Riverfall
        state.npc_parties.append(NPCParty("test_wolf_pack", "undead", "Dire Wolf Pack", 1, 0, [CombatSimulator.load_enemy("wolf")], behavior="idle"))

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
        tile = self.state.world.get_tile(q, r)
        if tile and tile.poi_id:
            loc = self.state.locations.get(tile.poi_id)
            if loc and not self.state.global_flags.get(f"seen_{tile.poi_id}"):
                self.state.global_flags[f"seen_{tile.poi_id}"] = True
                self.message_view.show("Discovery!", f"You have found {loc.name}, a {loc.location_type}. Its location is now marked on your map.")

    def on_random_encounter(self, q, r):
        tile = self.state.world.get_tile(q, r)
        biome = tile.terrain_type if tile else "plains"

        # Seeded RNG for deterministic encounters per hex
        encounter_seed = self.state.seed ^ (q * 3919) ^ (r * 7237)
        rng = RNGManager(encounter_seed)
        roll = rng.get_float()

        if biome == "forest":
            enemy_id = "wolf" if roll < 0.7 else "bandit"
        elif biome == "mountain":
            enemy_id = "skeleton"
        elif biome == "water":
            return # No water encounters for now
        else: # plains
            enemy_id = "orc" if roll < 0.5 else "bandit"

        enemy = CombatSimulator.load_enemy(enemy_id)
        self.logs.append(f"Encounter! A {enemy.name} blocks your path.")
        self.active_combat = {"enemies": [enemy], "turn": 1}
        self.pre_battle_active = True
        self.combat_log = [f"Battle against {enemy.name} initiated!"]

    def on_enter_location(self, poi_id):
        loc = self.state.locations.get(poi_id)
        if isinstance(loc, Town):
            self.trigger_transition("town")
            self.active_town = loc
            self.logs.append(f"Entered town: {loc.name}.")
        elif isinstance(loc, Dungeon):
            self.logs.append(f"Entering dungeon: {loc.name}!")
            gen = DungeonGenerator(self.state.seed + loc.q + loc.r)
            self.state.active_dungeon = gen.generate(40, 20)
            self.state.active_dungeon_id = poi_id
            self.state.dungeon_pos = self.state.active_dungeon.start_pos
            self.state.compute_fov()
        elif loc.location_type == "shrine":
            self.logs.append(f"You visited {loc.name}. The party feels blessed.")
            for m in self.state.party.members:
                m.morale = min(m.max_morale, m.morale + 20)
                m.stamina = min(m.max_stamina, m.max_stamina + 10)
        elif loc.location_type == "resource_node":
            amount = random.randint(10, 30)
            self.state.party.gold += amount
            self.logs.append(f"Scavenged {amount} gold from {loc.name}.")
        elif loc.location_type == "watchtower":
            self.logs.append(f"You climbed {loc.name}. Your view of the realm is greatly expanded.")
            self.state.compute_overworld_visibility()

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
        # Faction-specific ambience
        tile = self.state.world.get_tile(self.state.party.q, self.state.party.r)
        faction_id = tile.faction_influence if tile else "neutral"
        if faction_id == "undead":
            self.audio.play_ambient("undead_theme")
        elif faction_id == "bandits":
            self.audio.play_ambient("bandit_theme")
        else:
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
                        self.state.compute_overworld_visibility()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = True
            elif event.key == pygame.K_SPACE:
                old_food = self.state.party.food
                self.state.advance_turn()
                if old_food == 0 and self.state.party.food == 0:
                    self.logs.append("The party is starving! Morale and health are failing.")

                # Check NPC Encounters
                for npc in self.state.npc_parties:
                    if (npc.q, npc.r) == (self.state.party.q, self.state.party.r):
                        rel = self.state.faction_system.get_reputation(npc.faction_id)
                        if rel <= -50:
                            self.logs.append(f"Ambushed by {npc.name}!")
                            self.active_combat = {"enemies": npc.members, "turn": 1}
                            self.state.npc_parties.remove(npc)
                        else:
                            self.on_trigger_story_event("npc_meeting", title=f"Meeting: {npc.name}", desc=f"You encounter a group of {npc.name}. They seem {self.state.faction_system.get_status(npc.faction_id).lower()}.", choices=[{"text": "Trade Rumors", "outcome": {"type": "message", "text": "They share some local gossip."}}, {"text": "Leave", "outcome": {"type": "message", "text": "Safe travels."}}])

                # Check Timed Events
                new_timed = []
                for event_data in self.state.timed_events:
                    if event_data["trigger_turn"] <= self.state.turn:
                        self.on_trigger_story_event(event_data["event_id"])
                    else:
                        new_timed.append(event_data)
                self.state.timed_events = new_timed

                # Check Quest Deadlines
                for q_id, quest in self.state.quest_manager.quests.items():
                    if quest.is_active and not quest.is_finished and quest.deadline_turn:
                        if self.state.turn > quest.deadline_turn:
                            quest.is_finished = True
                            self.logs.append(f"QUEST FAILED: {quest.title} - The deadline has passed.")

                EventTrigger.check_wait()
                EventTrigger.check_time()
                self.logs.append(f"Turn {self.state.turn} begins.")
                if self.state.ironman:
                    SaveManager.save_game("data/saves/ironman.sav", self.world_settings)
            elif event.key == pygame.K_s:
                SaveManager.save_game("data/saves/quicksave.sav", self.world_settings)
                self.logs.append("Game saved.")
            elif event.key == pygame.K_l:
                if SaveManager.load_game("data/saves/quicksave.sav"):
                    self.world_settings = self.state.world_settings
                    self.world_gen = WorldGenerator(self.state.seed, self.world_settings)
                    self.logs.append("Game loaded.")
                else: self.logs.append("Failed to load save.")
            elif event.key == pygame.K_i:
                self.show_party_screen = True
            elif event.key == pygame.K_r:
                # Rest at camp
                if self.state.party.food >= len(self.state.party.members):
                    self.state.advance_turn()
                    self.logs.append("You set up camp and rest for the night.")
                else:
                    self.logs.append("Not enough food to set up camp.")

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

                    if tile.has_loot:
                        amount = random.randint(50, 150)
                        self.state.party.gold += amount
                        self.logs.append(f"You found a treasure chest! Gained {amount} gold.")
                        tile.has_loot = False

                    if hasattr(tile, 'enemies') and tile.enemies:
                        enemy_id = tile.enemies[0]
                        enemy = CombatSimulator.load_enemy(enemy_id)
                        self.logs.append(f"Dungeon Encounter! A {enemy.name} jumps from the shadows!")
                        self.active_combat = {"enemies": [enemy], "turn": 1}
                        self.pre_battle_active = True
                        self.combat_log = [f"Battle against {enemy.name} initiated!"]
                        tile.enemies = [] # Clear encounter

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
            action = self.combat_view.handle_click(event.pos, self.state.party.members)
            if action:
                if action == "retreat":
                    if random.random() < 0.6: # 60% chance to escape
                        self.logs.append("Party successfully retreated from battle!")
                        self.active_combat = None
                    else:
                        self.logs.append("Retreat failed! You are cornered!")
                        # Failed retreat triggers an enemy round where party can't act
                        res = CombatSimulator.simulate_round(self.state.party.members, self.active_combat["enemies"], self.active_combat["turn"], self.current_formation)
                        # Filter out party actions for this specific failed retreat penalty?
                        # Or just let it be a normal round. The design says "limited direct interventions".
                        # If I just pass members, they will attack.
                        # Let's just make it a normal round for now but log the failure.
                        self.combat_queue.extend(res["log"])
                        self.active_combat["turn"] += 1
                elif action == "pause":
                    self.combat_paused = not self.combat_paused
                elif action == "speed":
                    self.combat_speed = 2.0 if self.combat_speed == 1.0 else 1.0
                elif action == "tactics":
                    self.pre_battle_active = True
                else:
                    int_log = CombatSimulator.resolve_intervention(action, self.state.party.members, self.active_combat["enemies"])
                    self.combat_queue.extend(int_log)

    def update_combat_animation(self):
        if self.combat_paused: return

        # Auto-enqueue next round if queue empty
        if not self.combat_queue and self.active_combat:
            res = CombatSimulator.simulate_round(self.state.party.members, self.active_combat["enemies"], self.active_combat["turn"], self.current_formation)
            self.combat_queue.extend(res["log"])
            self.active_combat["turn"] += 1

        if not self.combat_queue: return

        self.combat_timer += 1 * self.combat_speed
        if self.combat_timer >= 15: # Roughly 0.5s at 30 FPS
            self.combat_timer = 0
            line = self.combat_queue.pop(0)
            self.combat_log.append(line)

            # Trigger FX
            if "attacks" in line:
                target_name = line.split("attacks ")[1].split(" for")[0]
                fx_pos = (700, 100) # Default enemy area
                if "Enemy" in line: fx_pos = (100, 100) # Party area

                # Find actual position
                if "Enemy" in line:
                    for idx, m in enumerate(self.state.party.members):
                        if m.name in target_name: fx_pos = (100, 100 + idx * 100); break
                else:
                    for idx, e in enumerate(self.active_combat["enemies"]):
                        if e.name in target_name: fx_pos = (700, 100 + idx * 100); break

                fx_type = "slash" if "attacks" in line else "spark"
                self.combat_view.effects.append((fx_type, fx_pos, 5))

            # If queue empty, check outcome
            if not self.combat_queue:
                if not any(e.hp > 0 for e in self.active_combat["enemies"]):
                    xp = len(self.active_combat["enemies"]) * 20
                    gold = sum(e.loot_gold for e in self.active_combat["enemies"])
                    self.state.party.gold += gold

                    summary_lines = [f"XP Gained: {xp}", f"Gold Found: {gold}", "Bonds strengthened between members."]
                    for m1 in self.state.party.members:
                        if m1.hp > 0:
                            if m1.gain_xp(xp):
                                summary_lines.append(f"{m1.name} LEVELED UP to {m1.level}!")
                            for m2 in self.state.party.members:
                                if m1 != m2 and m2.hp > 0:
                                    m1.adjust_relationship(m2.name, 2)

                    self.message_view.show("Combat Victory!", "\n".join(summary_lines))
                    self.logs.append(f"Combat Victory! Gained {xp} XP and {gold} Gold.")
                    self.active_combat = None
                elif not any(m.hp > 0 for m in self.state.party.members):
                    self.logs.append("Party Wiped Out...")
                    self.active_combat = None
                    self.game_over = True
                    self.victory = False

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
        elif node.service_type == "blacksmith":
            self.on_trigger_story_event("blacksmith_service", title="Blacksmith", desc="I can sharpen your blades for 30 gold, or craft something new if you have iron.", choices=[{"text": "Upgrade Weapons (30g)", "outcome": {"type": "message", "text": "Your weapons feel sharper."}}, {"text": "Craft Iron Shield (50g + Iron)", "outcome": {"type": "message", "text": "A sturdy shield is forged."}}, {"text": "Leave", "outcome": {"type": "message", "text": "Come back when you have coin."}}])
        elif node.service_type == "tavern":
            if self.state.party.gold >= 20:
                self.state.party.gold -= 20
                for m in self.state.party.members: m.stamina = m.max_stamina
                self.logs.append("Restored party stamina at the tavern.")
                # Rumor discovery
                from engine.lore_manager import LoreFragment
                frag = LoreFragment("rumor_1", "Whispers of the Deep", "They say the ruins to the south hold more than just gold.")
                if self.state.lore_manager.discover_fragment(frag):
                    self.logs.append("You heard an interesting rumor...")
                    self.message_view.show("New Rumor", frag.content)
            else: self.logs.append("Not enough gold for a round of drinks.")
        else:
            self.logs.append(f"Visited {node.name}. (Service not implemented)")

    def trigger_transition(self, target):
        self.transition_alpha = 255
        self.transition_target = target

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

                if self.game_running and self.paused:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.paused = False
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        action = self.pause_view.handle_click(event.pos)
                        if action == "resume": self.paused = False
                        elif action == "save_game":
                            SaveManager.save_game("data/saves/quicksave.sav", self.world_settings)
                            self.logs.append("Game saved.")
                        elif action == "load_game":
                            if SaveManager.load_game("data/saves/quicksave.sav"):
                                self.world_settings = self.state.world_settings
                                self.world_gen = WorldGenerator(self.state.seed, self.world_settings)
                                self.event_manager.load_quests("data/quests", self.state.quest_manager)
                                self.paused = False
                        elif action == "main_menu":
                            self.game_running = False
                            self.paused = False
                    continue

                if self.game_running and self.game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.end_view.handle_click(event.pos):
                            self.game_running = False
                            self.game_over = False
                            self.victory = False
                    continue

                if self.game_running and self.message_view.active_message:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.message_view.handle_click(event.pos)
                    continue

                if self.game_running and self.pre_battle_active:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        action = self.pre_battle_view.handle_click(event.pos)
                        if not action: continue

                        if action == "cycle_formation":
                            fl = list(FormationType)
                            self.current_formation = fl[(fl.index(self.current_formation) + 1) % len(fl)]
                        elif action == "start":
                            self.pre_battle_active = False
                            self.trigger_transition("combat")
                        elif "hero_" in action:
                            parts = action.split("_")
                            idx = int(parts[1])
                            field = parts[2]
                            hero = self.state.party.members[idx]
                            if field == "tactic":
                                opts = [t.value for t in TacticType]
                                hero.combat_tactic = opts[(opts.index(hero.combat_tactic) + 1) % len(opts)]
                            elif field == "priority":
                                opts = [p.value for p in AIPriority]
                                hero.combat_priority = opts[(opts.index(hero.combat_priority) + 1) % len(opts)]
                            elif field == "heal":
                                hero.heal_threshold = (hero.heal_threshold + 10) % 100
                    continue

                if not self.game_running:
                    if self.message_view.active_message:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.message_view.handle_click(event.pos)
                        continue

                    if event.type == pygame.KEYDOWN:
                        self.menu_view.handle_keydown(event)
                        continue

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        action = self.menu_view.handle_click(event.pos)
                        if action == "new_game":
                            # Loading Screen
                            self.screen.fill((10, 10, 15))
                            t_surf = pygame.font.SysFont("Arial", 24).render("Forging the Realm...", True, (255, 215, 0))
                            self.screen.blit(t_surf, (800 // 2 - t_surf.get_width() // 2, 600 // 2))
                            pygame.display.flip()

                            seed_val = self.menu_view.seed_input if self.menu_view.seed_input else None
                            self.state = self.setup_game(seed_val)
                            self.game_running = True
                            # Ensure starting area is fully loaded and discovered
                            self.check_chunks(self.state.party.q, self.state.party.r)
                            EventTrigger.check_enter_hex(self.state.party.q, self.state.party.r)
                            self.state.compute_overworld_visibility()
                            self.message_view.show("The Journey Begins", "You stand at the edge of Riverfall. The Unbound Realm stretches before you, filled with ancient secrets and growing dangers. Lead your party to glory or ruin.")
                        elif action == "load_game":
                            if SaveManager.load_game("data/saves/quicksave.sav"):
                                self.world_settings = self.state.world_settings
                                self.world_gen = WorldGenerator(self.state.seed, self.world_settings)
                                self.event_manager.load_quests("data/quests", self.state.quest_manager)
                                self.game_running = True
                        elif action == "settings":
                            self.message_view.show("Settings", "Difficulty: Balanced\nAudio: Enabled\n(More settings coming soon!)")
                        elif action == "quit":
                            pygame.quit(); sys.exit()
                    continue

                if self.active_event:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        idx = self.event_view.handle_click(event.pos)
                        if idx is not None: self.resolve_choice(idx)
                    continue
                if self.active_combat:
                    self.run_combat(event)
                    continue
                if self.show_party_screen:
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_i, pygame.K_ESCAPE]: self.show_party_screen = False
                        else: self.party_view.handle_keydown(event.key, self.state.party)
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.party_view.handle_click(event.pos, self.state.party): self.logs.append("Attribute increased!")
                    continue
                if self.active_town:
                    self.run_town(event)
                    continue
                elif self.state.active_dungeon:
                    self.run_dungeon(event)
                    continue
                else:
                    self.run_overworld(event)

            if not self.game_running:
                self.menu_view.render(self.screen)
                if self.message_view.active_message:
                    self.message_view.render(self.screen)
            elif self.game_over:
                self.end_view.render(self.screen, self.victory, self.state.turn)
            elif self.active_combat:
                if self.pre_battle_active:
                    self.pre_battle_view.render(self.screen, self.state.party.members, self.active_combat["enemies"], self.current_formation)
                else:
                    self.update_combat_animation()
                    if self.active_combat:
                        self.combat_view.render(self.screen, self.state.party.members, self.active_combat["enemies"], self.combat_log, self.active_combat["turn"], self.combat_paused, self.combat_speed)
            elif self.show_party_screen: self.party_view.render(self.screen, self.state.party)
            elif self.active_town: self.town_view.render(self.screen, self.active_town)
            elif self.state.active_dungeon: self.dungeon_view.render(self.screen, self.state.active_dungeon, self.state.dungeon_pos)
            else: self.overworld_view.render(self.screen, self.state.world, (self.state.party.q, self.state.party.r), self.logs)

            if self.game_running and self.active_event:
                self.event_view.render(self.screen, self.active_event)
            if self.game_running and self.message_view.active_message:
                self.message_view.render(self.screen)
            if self.game_running and self.paused:
                self.pause_view.render(self.screen)

            # Transition Overlay
            if self.transition_alpha > 0:
                overlay = pygame.Surface((800, 600))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(self.transition_alpha)
                self.screen.blit(overlay, (0, 0))
                self.transition_alpha = max(0, self.transition_alpha - 25)

            pygame.display.flip(); self.clock.tick(30)

if __name__ == "__main__":
    controller = GameController()
    controller.run()
