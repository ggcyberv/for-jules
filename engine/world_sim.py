import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class WorldEvent:
    description: str
    turn: int
    impact: Dict[str, any] = field(default_factory=dict)
    related_event_ids: List[int] = field(default_factory=list)
    event_id: int = 0

class EventManager:
    def __init__(self):
        self.events: List[WorldEvent] = []
        self.next_id = 1
        self.possible_events = [
            "A mysterious fog descends upon the valley.",
            "Rumors of a dragon sighting spread through the local taverns.",
            "A group of bandits has been spotted near the main trade route.",
            "An ancient tomb has been unearthed by a recent earthquake.",
            "The local lord has declared a week of celebration.",
            "A strange plague is affecting the livestock in nearby farms.",
            "A shooting star was seen, believed to be an omen of great change.",
            "Merchants report a shortage of rare spices due to sea monster attacks."
        ]

    def generate_random_event(self, turn: int) -> Optional[WorldEvent]:
        if random.random() < 0.3:  # 30% chance each tick
            desc = random.choice(self.possible_events)
            event = WorldEvent(description=desc, turn=turn, event_id=self.next_id)
            self.next_id += 1
            self.events.append(event)
            return event
        return None

    def get_event_log(self) -> List[str]:
        return [f"Turn {e.turn}: {e.description}" for e in self.events]
