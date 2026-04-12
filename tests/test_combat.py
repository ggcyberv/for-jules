import pytest
from engine.models import Stack, UnitType, Character, Stats
from engine.combat import resolve_combat

def test_resolve_combat_attacker_wins():
    hero_char = Character("Hero", "Fighter", Stats(18, 14, 16, 10, 10, 10), max_hp=100, current_hp=100)
    swordsman = UnitType("Swordsman", 5, 5, 20, 4, 4, 4, {"gold": 100}, 10, 1)
    party = [hero_char]
    garrison = [Stack(swordsman, 1, "s2")]

    result = resolve_combat(party, garrison, 1, 2)

    assert result.winner_id == 1

def test_resolve_combat_multi_stack():
    hero_char = Character("Hero", "Fighter", Stats(18, 14, 16, 10, 10, 10), max_hp=100, current_hp=100)
    swordsman = UnitType("Swordsman", 5, 5, 20, 4, 4, 4, {"gold": 100}, 10, 1)
    party = [hero_char]
    garrison = [Stack(swordsman, 2, "s3")]

    result = resolve_combat(party, garrison, 1, 2)

    assert result.winner_id == 1
