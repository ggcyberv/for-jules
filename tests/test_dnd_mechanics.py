import unittest
from engine.models import Character, Stats, Stack, UnitType
from engine.combat import resolve_combat

class TestDnDMechanics(unittest.TestCase):
    def test_initiative_dex_modifier(self):
        # We can't easily test the random roll, but we can verify the modifier logic is used
        char = Character("Test", "Fighter", stats=Stats(dexterity=14)) # +2 modifier
        self.assertEqual(char.get_modifier("dexterity"), 2)

    def test_combat_resolution(self):
        party = [Character("Hero", "Fighter", Stats(18, 18, 18, 10, 10, 10), max_hp=100, current_hp=100)]
        swordsman = UnitType("Swordsman", 5, 5, 5, 1, 1, 4, {"gold": 10}, 1, 1)
        garrison = [Stack(swordsman, 1)]

        result = resolve_combat(party, garrison, 1, 2)
        self.assertIn(result.winner_id, [1, 2])
        self.assertTrue(len(result.log) > 0)

if __name__ == '__main__':
    unittest.main()
