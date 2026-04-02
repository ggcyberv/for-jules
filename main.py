import sys
from engine.models import Player, Hero, POI, Stack, UnitType
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

    game_map.set_poi(town1)
    game_map.set_poi(mine1)
    game_map.set_poi(fort1)

    # Create players
    p1 = Player(1, "Player 1")
    h1 = Hero("Hero 1", 1, position=(0, 0), army=[Stack(swordsman, 20), Stack(archer, 10)])
    p1.heroes.append(h1)

    p2 = Player(2, "AI Opponent")
    h2 = Hero("Hero 2", 2, position=(9, 9), army=[Stack(swordsman, 15)])
    p2.heroes.append(h2)

    return GameManager(game_map, [p1, p2])

def main():
    manager = create_game()
    print("Welcome to the Turn-Based Strategy Game Prototype!")
    print("Commands: move x y, recruit unit qty, station unit qty direction, status, end, quit")
    print("Direction: to_poi or to_hero")

    while True:
        player = manager.current_player
        print(f"\n--- Turn {manager.turn_number} - {player.name}'s Turn ---")
        print(f"Resources: {player.resources}")
        print(f"Winning Streak: {player.winning_streak}")

        if not player.heroes:
            print("You have no heroes!")
            manager.next_turn()
            continue

        hero = player.heroes[0]
        tile = manager.game_map.get_tile(hero.position[0], hero.position[1])
        poi = tile.poi if tile else None

        print(f"Hero {hero.name} at {hero.position} (MP: {hero.movement_points})")
        if poi:
            owner_name = manager.players[poi.owner_id].name if poi.owner_id else "None"
            print(f"At {poi.poi_type} {poi.poi_id} (Owned by: {owner_name})")
            if poi.garrison:
                print(f"  Garrison: {[f'{s.quantity}x {s.unit_type.name}' for s in poi.garrison]}")

        print(f"Army: {[f'{s.quantity}x {s.unit_type.name}' for s in hero.army]}")

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
                        for entry in interaction['log'][-10:]:
                            print(f"  {entry}")
            except ValueError:
                print("Invalid coordinates.")
        elif action == "recruit" and len(cmd) == 3:
            if not poi:
                print("Not at a POI.")
                continue
            unit_name = cmd[1]
            try:
                qty = int(cmd[2])
                result = manager.recruit_units(hero, poi, unit_name, qty)
                print(result["message"])
            except ValueError:
                print("Invalid quantity.")
        elif action == "station" and len(cmd) == 4:
            if not poi:
                print("Not at a POI.")
                continue
            unit_name = cmd[1]
            try:
                qty = int(cmd[2])
                to_poi = cmd[3].lower() == "to_poi"
                result = manager.station_units(hero, poi, unit_name, qty, to_poi)
                print(result["message"])
            except ValueError:
                print("Invalid quantity.")
        elif action == "status":
            pass
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
