import pytest
from engine.models import Stack, UnitType
from engine.combat import resolve_combat

def test_resolve_combat_attacker_wins():
    swordsman = UnitType("Swordsman", 5, 5, 20, 4, 4, 4, {"gold": 100}, 10, 1)
    army1 = [Stack(swordsman, 100, "s1")]
    army2 = [Stack(swordsman, 10, "s2")]

    result = resolve_combat(army1, army2, 1, 2)

    assert result.winner_id == 1
    assert result.army2_losses["s2"] == 10

def test_resolve_combat_multi_stack():
    swordsman = UnitType("Swordsman", 5, 5, 20, 4, 4, 4, {"gold": 100}, 10, 1)
    # Two stacks of swordsmen for attacker
    army1 = [Stack(swordsman, 50, "s1"), Stack(swordsman, 50, "s2")]
    army2 = [Stack(swordsman, 10, "s3")]

    result = resolve_combat(army1, army2, 1, 2)

    assert result.winner_id == 1
    # Check that losses are attributed to the correct stacks
    assert result.army2_losses["s3"] == 10
    assert result.army1_losses["s1"] + result.army1_losses["s2"] >= 0
