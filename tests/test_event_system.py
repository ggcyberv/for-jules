import pytest
import os
import json
from engine.game_state import GameState
from events.event_template import EventManager, EventTemplate, EventChoice
from events.event_trigger import EventTrigger
from world.hex_grid import HexGrid
from party.party_manager import Party
from party.character import Character
from engine.event_bus import event_bus

@pytest.fixture
def state():
    state = GameState()
    grid = HexGrid(chunk_size=10)
    # Ensure starting chunk exists
    grid.get_tile(0, 0)
    party = Party(members=[Character("Test", race="Human")])
    state.initialize(grid, party, 123, {})
    return state

def test_event_matching(state):
    em = EventManager()

    # Category A Forest Event
    e1 = EventTemplate("e1", "Forest Event", "Desc", trigger_type="a", terrain_types=["forest"], severity=0.1)
    # Category A Plains Event
    e2 = EventTemplate("e2", "Plains Event", "Desc", trigger_type="a", terrain_types=["plains"], severity=0.1)

    em.add_template(e1)
    em.add_template(e2)

    # Forest context
    context = {"terrain": "forest", "danger": 0.1}
    matches = em.find_matching_events(state, "a", context)
    assert len(matches) == 1
    assert matches[0].event_id == "e1"

    # Plains context
    context = {"terrain": "plains", "danger": 0.1}
    matches = em.find_matching_events(state, "a", context)
    assert len(matches) == 1
    assert matches[0].event_id == "e2"

def test_severity_sorting(state):
    em = EventManager()
    e_low = EventTemplate("e_low", "Low", "Desc", trigger_type="a", severity=0.1)
    e_high = EventTemplate("e_high", "High", "Desc", trigger_type="a", severity=0.9)
    em.add_template(e_low)
    em.add_template(e_high)

    # High danger context
    context = {"terrain": "plains", "danger": 0.8}
    matches = em.find_matching_events(state, "a", context)
    assert matches[0].event_id == "e_high"

    # Low danger context
    context = {"terrain": "plains", "danger": 0.2}
    matches = em.find_matching_events(state, "a", context)
    assert matches[0].event_id == "e_low"

def test_event_trigger_generic(state):
    triggered = []
    def on_req(trigger_type, context):
        triggered.append((trigger_type, context))

    event_bus.subscribe("request_random_event", on_req)

    try:
        # Trigger Category A
        # Manually add tile since we are in a test without the generator
        from world.hex_grid import HexTile
        state.world.add_tile(HexTile(1, 1, terrain_type="plains", danger_rating=0.1))

        EventTrigger.check_enter_hex(1, 1)
        assert any(t[0] == "a" for t in triggered), f"Triggered were: {triggered}"

        # Trigger Category C
        EventTrigger.check_wait()
        assert any(t[0] == "c" for t in triggered)

        # Trigger Category E
        EventTrigger.check_leave_hex(1, 1)
        assert any(t[0] == "e" for t in triggered)
    finally:
        event_bus.unsubscribe("request_random_event", on_req)
