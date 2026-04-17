from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class LoreFragment:
    fragment_id: str
    title: str
    content: str
    faction_related: Optional[str] = None

class LoreManager:
    def __init__(self):
        self.discovered_fragments: List[LoreFragment] = []
        self.knowledge_level: int = 0

    def discover_fragment(self, fragment: LoreFragment):
        if fragment not in self.discovered_fragments:
            self.discovered_fragments.append(fragment)
            self.knowledge_level += 1
            return True
        return False
