import random
from typing import List, Dict, Any, Tuple
from party.character import Character
from combat.tactics import TacticType, TACTIC_EFFECTS

class CombatSimulator:
    @staticmethod
    def simulate_battle(party_members: List[Character], enemies: List[Character], tactic: TacticType = TacticType.BALANCED) -> Dict[str, Any]:
        log = []
        round_num = 1
        tactic_effect = TACTIC_EFFECTS[tactic]

        while any(m.hp > 0 for m in party_members) and any(e.hp > 0 for e in enemies) and round_num <= 20:
            log.append(f"Round {round_num}")

            # Combine and sort by speed for initiative
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
                    atk = unit.attack * tactic_effect.attack_mod
                    dfn = target.defense
                else:
                    targets = [m for m in party_members if m.hp > 0]
                    if not targets: break
                    target = random.choice(targets)
                    attacker_name, defender_name = "Enemy " + unit.name, target.name
                    atk = unit.attack
                    dfn = target.defense * tactic_effect.defense_mod

                damage = max(1, int(atk - (dfn // 2)))
                target.hp = max(0, target.hp - damage)
                log.append(f"{attacker_name} attacks {defender_name} for {damage} damage!")

                if target.hp <= 0:
                    log.append(f"{defender_name} falls!")

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
