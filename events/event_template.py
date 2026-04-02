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
        # In a real implementation, this would load JSON files from the directory
        # For Milestone 1, we register a sample event
        sample_choice1 = EventChoice("Investigate the whispers", {"type": "encounter", "enemy_type": "ghost"})
        sample_choice2 = EventChoice("Ignore and move on", {"type": "message", "text": "You walked away safely."})

        sample_event = EventTemplate(
            "crypt_whispers_01",
            "Whispers from the Crypt",
            "As you approach the ancient ruins, a chilling whisper fills the air...",
            [sample_choice1, sample_choice2]
        )
        self.templates[sample_event.event_id] = sample_event

    def get_event(self, event_id: str) -> Optional[EventTemplate]:
        return self.templates.get(event_id)
