import random
from typing import List, Dict, Any, Tuple, Optional
from party.character import Character, Affliction
from combat.tactics import TacticType, TACTIC_EFFECTS, FormationType, FORMATION_EFFECTS, AIPriority

class CombatSimulator:
    @staticmethod
    def simulate_battle(party_members: List[Character],
                        enemies: List[Character],
                        tactic: TacticType = TacticType.BALANCED,
                        formation: FormationType = FormationType.NONE,
                        priority: AIPriority = AIPriority.NEAREST) -> Dict[str, Any]:
        log = []
        round_num = 1
        t_effect = TACTIC_EFFECTS[tactic]
        f_effect = FORMATION_EFFECTS[formation]

        # Combine modifiers
        final_atk_mod = t_effect.attack_mod * f_effect.attack_mod
        final_def_mod = t_effect.defense_mod * f_effect.defense_mod
        final_spd_mod = t_effect.speed_mod * f_effect.speed_mod

        while any(m.hp > 0 for m in party_members) and any(e.hp > 0 for e in enemies) and round_num <= 20:
            log.append(f"Round {round_num}")

            all_units = [(m, "party") for m in party_members if m.hp > 0] + \
                        [(e, "enemy") for e in enemies if e.hp > 0]
            all_units.sort(key=lambda x: x[0].speed * (final_spd_mod if x[1] == "party" else 1.0), reverse=True)

            for unit, side in all_units:
                if unit.hp <= 0: continue

                if side == "party":
                    targets = [e for e in enemies if e.hp > 0]
                    if not targets: break

                    # Targeting Priority
                    if priority == AIPriority.WOUNDED:
                        target = min(targets, key=lambda x: x.hp)
                    else:
                        target = random.choice(targets)

                    attacker_name, defender_name = unit.name, target.name
                    atk = unit.effective_attack * final_atk_mod
                    dfn = target.defense
                else:
                    targets = [m for m in party_members if m.hp > 0]
                    if not targets: break
                    target = random.choice(targets)
                    attacker_name, defender_name = "Enemy " + unit.name, target.name
                    atk = unit.attack
                    dfn = target.effective_defense * final_def_mod

                damage = max(1, int(atk - (dfn // 2)))
                target.hp = max(0, target.hp - damage)
                log.append(f"{attacker_name} attacks {defender_name} for {damage} damage!")

                if target.hp <= 0:
                    log.append(f"{defender_name} falls!")
                    if side == "enemy":
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
        if random.random() < 0.4:
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
            target_list = [e for e in enemies if e.hp > 0]
            if target_list:
                target = random.choice(target_list)
                dmg = 15
                target.hp = max(0, target.hp - dmg)
                log.append(f"Divine intervention: Smited {target.name} for {dmg} damage!")
        return log
