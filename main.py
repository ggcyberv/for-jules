import sys
from engine.models import Player, Hero, POI, Stack, UnitType, Character, Stats
from engine.map import GameMap
from engine.manager import GameManager

def create_game():
    # Define unit types
    swordsman = UnitType("Swordsman", 5, 5, 20, 3, 5, 4, {"gold": 100}, 10, 1)
    archer = UnitType("Archer", 6, 3, 15, 2, 6, 6, {"gold": 120}, 12, 1)

    # Create map
    game_map = GameMap(10, 10)

    # Create POIs
    town1 = POI("town1", "town", (1, 1), 5, income={"gold": 200}, recruitable_units=[swordsman, archer])
    mine1 = POI("mine1", "mine", (3, 3), 1, income={"gold": 50})
    fort1 = POI("fort1", "fort", (5, 5), 2, garrison=[Stack(swordsman, 10)])
    dungeon1 = POI("dungeon1", "dungeon", (7, 7), 3, garrison=[Stack(swordsman, 5), Stack(archer, 5)])

    game_map.set_poi(town1)
    game_map.set_poi(mine1)
    game_map.set_poi(fort1)
    game_map.set_poi(dungeon1)

    # Create players
    p1 = Player(1, "Player 1")
    player_char = Character("Valeria", "Fighter", Stats(16, 12, 14, 10, 10, 10), max_hp=30, current_hp=30)
    h1 = Hero("Party 1", 1, position=(0, 0), party=[player_char])
    p1.heroes.append(h1)

    p2 = Player(2, "AI Opponent")
    ai_char = Character("Grok", "Orc", Stats(18, 10, 16, 8, 8, 8), max_hp=40, current_hp=40)
    h2 = Hero("Enemy Party", 2, position=(9, 9), party=[ai_char])
    p2.heroes.append(h2)

    return GameManager(game_map, [p1, p2])

def main():
    manager = create_game()
    print("Welcome to the D&D World Simulator!")
    print("Commands: move x y, note [text...], status, log, party, end, quit")

    while True:
        player = manager.current_player
        print(f"\n--- Turn {manager.turn_number} - {player.name}'s Turn ---")

        if not player.heroes:
            print("You have no party!")
            manager.next_turn()
            continue

        hero = player.heroes[0]
        # Discover area around hero
        manager.game_map.discover_area(hero.position[0], hero.position[1], 2)

        tile = manager.game_map.get_tile(hero.position[0], hero.position[1])
        poi = tile.poi if tile else None

        print(f"Party {hero.name} at {hero.position} (MP: {hero.movement_points})")
        if poi:
            owner_name = manager.players[poi.owner_id].name if poi.owner_id else "None"
            print(f"At {poi.poi_type} {poi.poi_id} (Owned by: {owner_name})")
            if poi.garrison:
                print(f"  Garrison: {[f'{s.quantity}x {s.unit_type.name}' for s in poi.garrison]}")

        print(f"Party: {[f'{c.name} ({c.char_class}) HP: {c.current_hp}/{c.max_hp}' for c in hero.party]}")
        if tile.notes:
            print(f"Notes: {tile.notes}")

        try:
            line = sys.stdin.readline()
            if not line: break
            cmd = line.strip().split()
        except EOFError:
            break

        if not cmd: continue

        action = cmd[0].lower()
        if action == "move" and len(cmd) == 3:
            try:
                x, y = int(cmd[1]), int(cmd[2])
                result = manager.move_hero(hero, (x, y))
                print(result["message"])
                if result.get("interaction"):
                    interaction = result['interaction']
                    if interaction.get('message'):
                        print(f"Interaction: {interaction['message']}")
                    elif interaction.get('type'):
                        print(f"Interaction: {interaction['type']}")

                    if interaction.get('log'):
                        print("Combat Log:")
                        for entry in interaction['log'][-20:]:
                            print(f"  {entry}")
            except ValueError:
                print("Invalid coordinates.")
        elif action == "note" and len(cmd) > 1:
            note_text = " ".join(cmd[1:])
            tile.notes.append(note_text)
            print("Note added.")
        elif action == "log":
            print("\n--- Game Log ---")
            for entry in manager.game_log:
                print(f"  {entry}")
        elif action == "party":
            for c in hero.party:
                print(f"{c.name} ({c.char_class}) Lvl {c.level}")
                print(f"  STR: {c.stats.strength} DEX: {c.stats.dexterity} CON: {c.stats.constitution}")
                print(f"  INT: {c.stats.intelligence} WIS: {c.stats.wisdom} CHA: {c.stats.charisma}")
                print(f"  HP: {c.current_hp}/{c.max_hp}  XP: {c.experience}")
        elif action == "status":
            print(f"Resources: {player.resources}")
            print(f"Owned POIs: {player.owned_pois}")
        elif action == "end":
            manager.next_turn()
            if player.winning_streak >= manager.win_streak_required:
                print(f"\nCongratulations! {player.name} wins!")
                break
        elif action == "quit":
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
