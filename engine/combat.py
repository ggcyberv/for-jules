import random
from typing import List, Tuple, Dict, Any, Optional, Union
from dataclasses import dataclass
from engine.models import Character, Stack

@dataclass
class CombatResult:
    winner_id: Optional[int]
    log: List[str]
    xp_reward: int = 0

def resolve_combat(party: List[Character], garrison: List[Stack], owner1_id: int, owner2_id: int) -> CombatResult:
    log = []

    # Convert garrison stacks to temporary Character-like objects for tactical combat
    # We'll track which stack each enemy belongs to
    enemies = []
    stack_map = {} # enemy character -> stack
    for stack in garrison:
        for i in range(stack.quantity):
            enemy = Character(
                name=f"{stack.unit_type.name} {i+1}",
                char_class="Monster",
                max_hp=stack.unit_type.health,
                current_hp=stack.unit_type.health,
                level=1 # Simplified
            )
            enemies.append(enemy)
            stack_map[enemy] = stack

    combatants = []
    for char in party:
        combatants.append(('party', char, random.randint(1, 20) + char.get_modifier("dexterity")))
    for enemy in enemies:
        combatants.append(('enemy', enemy, random.randint(1, 20))) # Simplified initiative

    # Sort by initiative
    combatants.sort(key=lambda x: x[2], reverse=True)

    log.append("Combat Start!")

    round_num = 1
    while any(c.current_hp > 0 for side, c, init in combatants if side == 'party') and \
          any(c.current_hp > 0 for side, c, init in combatants if side == 'enemy') and \
          round_num <= 50:

        log.append(f"Round {round_num}")
        for side, char, init in combatants:
            if char.current_hp <= 0:
                continue

            # Choose target
            targets = [c for s, c, i in combatants if s != side and c.current_hp > 0]
            if not targets:
                break

            target = random.choice(targets)

            # Hit roll
            roll = random.randint(1, 20)
            attack_bonus = char.get_modifier("strength") if side == 'party' else 0
            if roll + attack_bonus >= target.ac:
                # Damage roll
                damage = random.randint(1, 8) + (char.get_modifier("strength") if side == 'party' else 0)
                if damage < 1: damage = 1
                target.current_hp -= damage
                log.append(f"{char.name} hits {target.name} for {damage} damage! ({target.current_hp}/{target.max_hp} HP)")
                if target.current_hp <= 0:
                    log.append(f"{target.name} has been defeated!")
            else:
                log.append(f"{char.name} misses {target.name} (rolled {roll+attack_bonus} vs AC {target.ac})")

        round_num += 1

    winner_id = None
    if any(c.current_hp > 0 for side, c, init in combatants if side == 'party'):
        winner_id = owner1_id
        log.append("Party wins!")
    else:
        winner_id = owner2_id
        log.append("Party was defeated!")

    # Update garrison stacks based on remaining enemies
    for stack in garrison:
        stack.quantity = 0
    for side, char, init in combatants:
        if side == 'enemy' and char.current_hp > 0:
            stack_map[char].quantity += 1

    # Remove empty stacks
    garrison[:] = [s for s in garrison if s.quantity > 0]

    return CombatResult(
        winner_id=winner_id,
        log=log,
        xp_reward=len(enemies) * 50
    )
