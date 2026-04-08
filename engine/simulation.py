import random
from typing import Dict, Any, List, Optional
from party.character import Character
from engine.event_bus import event_bus

class WorldSimulation:
    def __init__(self):
        self.tick_count = 0
        self.npc_witness_radius = 2 # hexes

    def tick(self):
        from engine.game_state import GameState
        state = GameState()
        self.tick_count += 1

        # 1. Environment update
        self._update_environment(state)

        # 2. NPC Autonomous Actions
        for npc_party in state.npc_parties:
            for npc in npc_party.members:
                if not isinstance(npc, Character): continue

                self._update_needs(npc)

                if npc.current_activity is None or npc.current_activity.get("progress", 0) >= 1.0:
                    if npc.current_activity and npc.current_activity.get("progress", 0) >= 1.0:
                        self._resolve_activity_outcome(npc, npc_party, state)

                    next_action = self._decide_next_action(npc, npc_party, state)
                    self._start_activity(npc, next_action)
                else:
                    self._progress_activity(npc)

        # 3. Spontaneous events
        if random.random() < 0.01: # 1% chance per tick
            self._generate_spontaneous_event(state)

    def _update_environment(self, state):
        if self.tick_count % 24 == 0:
            if random.random() < 0.2:
                state.current_weather = random.choice(["Rainy", "Foggy", "Stormy", "Clear"])

    def _update_needs(self, npc: Character):
        # Needs increase over time
        npc.needs["hunger"] = min(1.0, npc.needs["hunger"] + 0.05)
        npc.needs["thirst"] = min(1.0, npc.needs["thirst"] + 0.08)
        npc.needs["sleep"] = min(1.0, npc.needs["sleep"] + 0.03)
        npc.needs["social"] = min(1.0, npc.needs["social"] + 0.04)

    def _decide_next_action(self, npc: Character, party, state) -> str:
        # Advanced Utility-based decision: Needs vs Goals
        urgency = {
            'eat': npc.needs["hunger"] * 1.5,
            'drink': npc.needs["thirst"] * 2.0,
            'sleep': npc.needs["sleep"] * 1.2,
            'socialize': npc.needs["social"] * (1.0 + npc.goals.get("power", 0)),
            'work': npc.goals.get("wealth", 0) * 0.8,
            'defend': npc.goals.get("safety", 0) * (1.0 - npc.needs["sleep"]),
            'wander': 0.2 + (npc.goals.get("power", 0) * 0.5)
        }

        # Weight by personality
        if "greedy" in npc.personality_traits: urgency["work"] *= 1.5
        if "aggressive" in npc.personality_traits: urgency["wander"] *= 1.5
        if "coward" in npc.personality_traits: urgency["defend"] *= 2.0

        # Critical needs override goals
        if npc.needs["hunger"] > 0.8: urgency["eat"] += 2.0
        if npc.needs["thirst"] > 0.8: urgency["drink"] += 3.0

        best_action = max(urgency, key=urgency.get)
        return best_action

    def _start_activity(self, npc: Character, action: str):
        durations = {
            "eat": 0.5, "drink": 0.2, "sleep": 2.0, "socialize": 0.8,
            "wander": 1.0, "work": 2.0, "defend": 1.5
        }
        npc.current_activity = {
            "action": action,
            "progress": 0.0,
            "speed": 1.0 / durations.get(action, 1.0)
        }

    def _progress_activity(self, npc: Character):
        if npc.current_activity:
            npc.current_activity["progress"] += npc.current_activity["speed"]

    def _resolve_activity_outcome(self, npc: Character, party, state):
        action = npc.current_activity["action"]
        outcome_text = ""

        if action == "eat":
            npc.needs["hunger"] = 0.0
            outcome_text = f"{npc.name} found some food and ate."
        elif action == "drink":
            npc.needs["thirst"] = 0.0
            outcome_text = f"{npc.name} quenched their thirst."
        elif action == "sleep":
            npc.needs["sleep"] = 0.0
            outcome_text = f"{npc.name} woke up feeling refreshed."
        elif action == "socialize":
            npc.needs["social"] = 0.0
            npc.last_social_tick = self.tick_count
            outcome_text = f"{npc.name} shared some stories with others."
        elif action == "work":
            # Gaining wealth
            gold_gain = random.randint(5, 15)
            # In a real DF sim, this would involve a location/job
            outcome_text = f"{npc.name} finished a day of work and earned {gold_gain} gold."
        elif action == "defend":
            outcome_text = f"{npc.name} spent time fortifying their position."
        elif action == "wander":
            neighbors = state.world.get_neighbors(party.q, party.r)
            if neighbors:
                party.q, party.r = random.choice(neighbors)
                outcome_text = f"{npc.name} wandered into a new area."
        elif action == "trade":
            # Find nearest town and move towards it or trade if already there
            outcome_text = f"{npc.name} engaged in trade."

        if outcome_text:
            self._generate_simulation_event(npc, action, outcome_text, party.q, party.r, state)

        npc.current_activity = None

    def _generate_simulation_event(self, actor, action_type, description, q, r, state):
        from engine.game_state import WorldFact
        event = WorldFact(
            fact_id=f"sim_{actor.name}_{action_type}_{state.turn}_{self.tick_count}",
            turn_recorded=state.turn,
            actors=[actor.name],
            description=description,
            data={"q": q, "r": r, "type": action_type}
        )
        state.world_facts.append(event)

        # Perception check
        if state.party:
            dist = state.world.distance(state.party.q, state.party.r, q, r)
            if dist <= self.npc_witness_radius:
                event_bus.publish("trigger_story_event", event_id=None, title="Observation", desc=description)

    def _generate_spontaneous_event(self, state):
        from engine.game_state import WorldFact
        events = [
            {"title": "Meteor Shower", "desc": "Bright streaks of light fill the night sky."},
            {"title": "Earthquake", "desc": "The ground trembles beneath your feet."},
            {"title": "Heavy Fog", "desc": "A thick, unnatural fog rolls in across the realm."}
        ]
        evt = random.choice(events)

        fact = WorldFact(
            fact_id=f"spontaneous_{state.turn}_{self.tick_count}",
            turn_recorded=state.turn,
            actors=[],
            description=evt["desc"]
        )
        state.world_facts.append(fact)
        event_bus.publish("trigger_story_event", event_id=None, title=evt["title"], desc=evt["desc"])
