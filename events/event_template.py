import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

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
                        conditions=data.get("conditions", {})
                    )
                    self.templates[event_id] = template

    def get_event(self, event_id: str) -> Optional[EventTemplate]:
        return self.templates.get(event_id)

    def add_template(self, template: EventTemplate):
        self.templates[template.event_id] = template
