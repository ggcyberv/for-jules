from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class QuestObjective:
    description: str
    target_id: str
    target_count: int = 1
    current_count: int = 0
    is_complete: bool = False

@dataclass
class Quest:
    quest_id: str
    title: str
    description: str
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = False
    is_finished: bool = False

class QuestManager:
    def __init__(self):
        self.quests: Dict[str, Quest] = {}

    def add_quest(self, quest: Quest):
        self.quests[quest.quest_id] = quest

    def start_quest(self, quest_id: str):
        if quest_id in self.quests:
            self.quests[quest_id].is_active = True

    def update_objective(self, target_id: str, amount: int = 1):
        for quest in self.quests.values():
            if quest.is_active and not quest.is_finished:
                for obj in quest.objectives:
                    if obj.target_id == target_id:
                        obj.current_count += amount
                        if obj.current_count >= obj.target_count:
                            obj.is_complete = True

                if all(obj.is_complete for obj in quest.objectives):
                    quest.is_finished = True
                    # Reward handled by controller/consequence engine
                    return quest
        return None
