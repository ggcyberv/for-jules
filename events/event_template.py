import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from engine.quest_manager import Quest, QuestObjective

@dataclass
class EventChoice:
    text: str
    outcome: Dict[str, Any]
    skill_check: Optional[str] = None

@dataclass
class EventTemplate:
    event_id: str
    title: str
    description: str
    choices: List[EventChoice] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    trigger_type: str = "enter"  # a, b, c, d, e, f
    terrain_types: List[str] = field(default_factory=list)
    danger_min: float = 0.0
    danger_max: float = 1.0
    faction: str = "any"
    severity: float = 0.5
    impact_rating: int = 1

    def check_conditions(self, state, context: Dict[str, Any] = None) -> bool:
        """Checks if the global state meets all conditions for this event."""
        for cond_key, cond_val in self.conditions.items():
            if cond_key == "min_gold" and state.party.gold < cond_val:
                return False
            if cond_key == "min_turn" and state.turn < cond_val:
                return False
            if cond_key == "max_turn" and state.turn > cond_val:
                return False
            if cond_key == "required_flag" and not state.global_flags.get(cond_val):
                return False
            if cond_key == "forbidden_flag" and state.global_flags.get(cond_val):
                return False
            if cond_key == "min_rep":
                faction_id, min_val = cond_val.get("faction"), cond_val.get("value")
                if state.faction_system.get_reputation(faction_id) < min_val:
                    return False
            if cond_key == "fact_occurred":
                if not any(f.fact_id == cond_val for f in state.world_facts):
                    return False
            if cond_key == "required_item" and state.party:
                if not any(item.name == cond_val for item in state.party.inventory):
                    return False

        # Check environment if context provided
        if context:
            terrain = context.get("terrain")
            if self.terrain_types and terrain not in self.terrain_types:
                return False

            danger = context.get("danger", 0.0)
            if danger < self.danger_min or danger > self.danger_max:
                return False

            faction = context.get("faction", "neutral")
            if self.faction != "any" and self.faction != faction:
                return False

        return True

class EventManager:
    def __init__(self):
        self.templates: Dict[str, EventTemplate] = {}

    def load_templates(self, directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            return

        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                with open(os.path.join(directory, filename), "r") as f:
                    data = json.load(f)
                    event_id = data.get("event_id")
                    choices = [
                        EventChoice(
                            text=c.get("text"),
                            outcome=c.get("outcome"),
                            skill_check=c.get("skill_check")
                        ) for c in data.get("choices", [])
                    ]
                    template = EventTemplate(
                        event_id=event_id,
                        title=data.get("title"),
                        description=data.get("description"),
                        choices=choices,
                        conditions=data.get("conditions", {}),
                        trigger_type=data.get("trigger_type", "enter"),
                        terrain_types=data.get("terrain_types", []),
                        danger_min=data.get("danger_min", 0.0),
                        danger_max=data.get("danger_max", 1.0),
                        faction=data.get("faction", "any"),
                        severity=data.get("severity", 0.5),
                        impact_rating=data.get("impact_rating", 1)
                    )
                    self.templates[event_id] = template

    def find_matching_events(self, state, trigger_type: str, context: Dict[str, Any]) -> List[EventTemplate]:
        """Finds all events that match the current state and trigger criteria."""
        eligible = []
        for template in self.templates.values():
            if template.trigger_type == trigger_type:
                if template.check_conditions(state, context):
                    eligible.append(template)

        # Sort by severity/impact matching the danger level if applicable
        danger = context.get("danger", 0.5)
        eligible.sort(key=lambda e: abs(e.severity - danger))

        return eligible

    def load_quests(self, directory: str, quest_manager):
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            return

        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                with open(os.path.join(directory, filename), "r") as f:
                    data = json.load(f)
                    objectives = [
                        QuestObjective(
                            description=o.get("description"),
                            target_id=o.get("target_id"),
                            target_count=o.get("target_count", 1)
                        ) for o in data.get("objectives", [])
                    ]
                    quest = Quest(
                        quest_id=data.get("quest_id"),
                        title=data.get("title"),
                        description=data.get("description"),
                        objectives=objectives,
                        rewards=data.get("rewards", {})
                    )
                    quest_manager.add_quest(quest)

    def get_event(self, event_id: str) -> Optional[EventTemplate]:
        return self.templates.get(event_id)

    def add_template(self, template: EventTemplate):
        self.templates[template.event_id] = template
