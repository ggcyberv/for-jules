import random
from typing import List, Dict, Any, Tuple, Optional
from party.character import Character, Affliction
from combat.tactics import TacticType, TACTIC_EFFECTS

class CombatSimulator:
    @staticmethod
    def simulate_battle(party_members: List[Character], enemies: List[Character], tactic: TacticType = TacticType.BALANCED) -> Dict[str, Any]:
        log = []
        round_num = 1
        tactic_effect = TACTIC_EFFECTS[tactic]

        while any(m.hp > 0 for m in party_members) and any(e.hp > 0 for e in enemies) and round_num <= 20:
            log.append(f"Round {round_num}")

            all_units = [(m, "party") for m in party_members if m.hp > 0] + \
                        [(e, "enemy") for e in enemies if e.hp > 0]
            all_units.sort(key=lambda x: x[0].speed * (tactic_effect.speed_mod if x[1] == "party" else 1.0), reverse=True)

            for unit, side in all_units:
                if unit.hp <= 0: continue

                if side == "party":
                    targets = [e for e in enemies if e.hp > 0]
                    if not targets: break
                    target = random.choice(targets)
                    attacker_name, defender_name = unit.name, target.name
                    atk = unit.effective_attack * tactic_effect.attack_mod
                    dfn = target.defense
                else:
                    targets = [m for m in party_members if m.hp > 0]
                    if not targets: break
                    target = random.choice(targets)
                    attacker_name, defender_name = "Enemy " + unit.name, target.name
                    atk = unit.attack
                    dfn = target.effective_defense * tactic_effect.defense_mod

                damage = max(1, int(atk - (dfn // 2)))
                target.hp = max(0, target.hp - damage)
                log.append(f"{attacker_name} attacks {defender_name} for {damage} damage!")

                if target.hp <= 0:
                    log.append(f"{defender_name} falls!")
                    if side == "enemy": # Party member falls
                        CombatSimulator._check_for_injury(target, log)

            round_num += 1

        victory = any(m.hp > 0 for m in party_members) and not any(e.hp > 0 for e in enemies)
        xp_gained = 0
        if victory:
            xp_gained = len(enemies) * 20
            for member in party_members:
                if member.hp > 0:
                    member.gain_xp(xp_gained)

        return {
            "victory": victory,
            "log": log,
            "xp_reward": xp_gained
        }

    @staticmethod
    def _check_for_injury(character: Character, log: List[str]):
        if random.random() < 0.4: # 40% chance of injury when falling
            injuries = [
                Affliction("Broken Arm", {"attack": 3}),
                Affliction("Concussion", {"attack": 2, "defense": 2}),
                Affliction("Limp", {"speed": 2})
            ]
            injury = random.choice(injuries)
            character.afflictions.append(injury)
            log.append(f"SEVERE: {character.name} sustained an injury: {injury.name}!")

    @staticmethod
    def resolve_intervention(action_type: str, party_members: List[Character], enemies: List[Character]):
        log = []
        if action_type == "heal":
            target = min(party_members, key=lambda m: m.hp / m.max_hp)
            heal_amt = 20
            target.hp = min(target.max_hp, target.hp + heal_amt)
            log.append(f"Divine intervention: {target.name} healed for {heal_amt} HP!")
        elif action_type == "strike":
            target = random.choice([e for e in enemies if e.hp > 0])
            dmg = 15
            target.hp = max(0, target.hp - dmg)
            log.append(f"Divine intervention: Smited {target.name} for {dmg} damage!")
        return log
