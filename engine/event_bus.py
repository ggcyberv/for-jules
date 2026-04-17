from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)

    def publish(self, event_type: str, **kwargs):
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(**kwargs)

# Global event bus instance
event_bus = EventBus()
