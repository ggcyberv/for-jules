import random
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from engine.models import Stack, UnitType

@dataclass
class CombatResult:
    winner_id: Optional[int]
    army1_losses: Dict[str, int] # stack_id -> quantity lost
    army2_losses: Dict[str, int] # stack_id -> quantity lost
    log: List[str]
    xp_reward: int = 0

def resolve_combat(army1: List[Stack], army2: List[Stack], owner1_id: int, owner2_id: int) -> CombatResult:
    # Deep copy armies to simulate combat
    a1 = [Stack(s.unit_type, s.quantity, s.stack_id) for s in army1]
    a2 = [Stack(s.unit_type, s.quantity, s.stack_id) for s in army2]

    a1_initial = {s.stack_id: s.quantity for s in army1}
    a2_initial = {s.stack_id: s.quantity for s in army2}

    # Track top unit HP for each stack
    a1_top_hp = {s.stack_id: s.unit_type.health for s in a1}
    a2_top_hp = {s.stack_id: s.unit_type.health for s in a2}

    log = []
    round_num = 1
    total_killed_value = 0

    while a1 and a2 and round_num <= 100:
        log.append(f"Round {round_num}")

        # Determine turn order based on speed
        all_stacks = []
        for i, s in enumerate(a1):
            all_stacks.append(('a1', i, s))
        for i, s in enumerate(a2):
            all_stacks.append(('a2', i, s))

        all_stacks.sort(key=lambda x: x[2].unit_type.speed, reverse=True)

        for side, idx, stack in all_stacks:
            if stack.quantity <= 0:
                continue

            if side == 'a1':
                if not a2: break
                target_idx = random.randint(0, len(a2) - 1)
                target = a2[target_idx]
                target_top_hp = a2_top_hp
                attacker_side, defender_side = "Attacker", "Defender"
            else:
                if not a1: break
                target_idx = random.randint(0, len(a1) - 1)
                target = a1[target_idx]
                target_top_hp = a1_top_hp
                attacker_side, defender_side = "Defender", "Attacker"

            # Calculate damage
            atk = stack.unit_type.attack
            dfn = target.unit_type.defense
            base_dmg = random.randint(stack.unit_type.damage_min, stack.unit_type.damage_max)

            damage_multiplier = 1.0 + (atk - dfn) * 0.05
            if damage_multiplier < 0.1: damage_multiplier = 0.1

            total_damage = int(stack.quantity * base_dmg * damage_multiplier)

            # Apply damage to top unit and then the rest of the stack
            current_top_hp = target_top_hp[target.stack_id]

            if total_damage >= current_top_hp:
                remaining_damage = total_damage - current_top_hp
                units_killed = 1 + (remaining_damage // target.unit_type.health)
                if units_killed >= target.quantity:
                    units_killed = target.quantity
                    target_top_hp[target.stack_id] = 0
                else:
                    target_top_hp[target.stack_id] = target.unit_type.health - (remaining_damage % target.unit_type.health)
            else:
                units_killed = 0
                target_top_hp[target.stack_id] -= total_damage

            target.quantity -= units_killed
            if side == 'a1': total_killed_value += units_killed * target.unit_type.health

            log.append(f"{attacker_side} {stack.unit_type.name} hits {defender_side} {target.unit_type.name} for {total_damage} damage, killing {units_killed} units.")

            # Remove dead stacks
            if target.quantity <= 0:
                log.append(f"{defender_side} {target.unit_type.name} stack destroyed!")
                if side == 'a1':
                    a2.pop(target_idx)
                else:
                    a1.pop(target_idx)

        round_num += 1

    winner_id = None
    if not a2 and a1:
        winner_id = owner1_id
        log.append("Attacker wins!")
    elif not a1 and a2:
        winner_id = owner2_id
        log.append("Defender wins!")
    else:
        log.append("Battle ends in a draw!")

    # Calculate losses
    def get_losses(initial_dict, remaining):
        losses = {}
        remaining_dict = {s.stack_id: s.quantity for s in remaining}
        for stack_id, initial_qty in initial_dict.items():
            rem_qty = remaining_dict.get(stack_id, 0)
            lost_qty = initial_qty - rem_qty
            losses[stack_id] = lost_qty
        return losses

    return CombatResult(
        winner_id=winner_id,
        army1_losses=get_losses(a1_initial, a1),
        army2_losses=get_losses(a2_initial, a2),
        log=log,
        xp_reward=total_killed_value // 10
    )
