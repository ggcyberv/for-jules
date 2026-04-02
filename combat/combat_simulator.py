import random
import json
import os
from typing import List, Dict, Any, Tuple, Optional
from party.character import Character, Affliction
from combat.tactics import TacticType, TACTIC_EFFECTS, FormationType, FORMATION_EFFECTS, AIPriority

class CombatSimulator:
    @staticmethod
    def load_enemy(enemy_id: str) -> Character:
        path = f"data/enemies/{enemy_id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return Character(
                    name=data["name"],
                    hp=data["hp"],
                    max_hp=data["hp"],
                    attack=data["attack"],
                    defense=data["defense"],
                    speed=data["speed"]
                )
        return Character("Unknown", hp=20, attack=5, defense=5, speed=3)

    @staticmethod
    def simulate_battle(party_members: List[Character],
                        enemies: List[Character],
                        tactic: TacticType = TacticType.BALANCED,
                        formation: FormationType = FormationType.NONE,
                        priority: AIPriority = AIPriority.NEAREST) -> Dict[str, Any]:
        log = []
        round_num = 1
        while any(m.hp > 0 for m in party_members) and any(e.hp > 0 for e in enemies) and round_num <= 20:
            round_res = CombatSimulator.simulate_round(party_members, enemies, round_num, tactic, formation, priority)
            log.extend(round_res["log"])
            round_num += 1

        victory = any(m.hp > 0 for m in party_members) and not any(e.hp > 0 for e in enemies)
        xp_reward = 0
        if victory:
            xp_reward = len(enemies) * 20
            for member in party_members:
                if member.hp > 0:
                    member.gain_xp(xp_reward)
        xp_gained = 0
        if victory:
            xp_gained = len(enemies) * 20
            for member in party_members:
                if member.hp > 0:
                    member.gain_xp(xp_gained)
                    member.combat_log.append(f"Victory against {len(enemies)} enemies. Gained {xp_gained} XP.")

        return {
            "victory": victory,
            "log": log,
            "xp_reward": xp_gained
        }

    @staticmethod
    def simulate_round(party_members: List[Character],
                       enemies: List[Character],
                       round_num: int,
                       tactic: TacticType = TacticType.BALANCED,
                       formation: FormationType = FormationType.NONE,
                       priority: AIPriority = AIPriority.NEAREST) -> Dict[str, Any]:
        log = [f"Round {round_num}"]
        t_effect = TACTIC_EFFECTS[tactic]
        f_effect = FORMATION_EFFECTS[formation]

        final_atk_mod = t_effect.attack_mod * f_effect.attack_mod
        final_def_mod = t_effect.defense_mod * f_effect.defense_mod
        final_spd_mod = t_effect.speed_mod * f_effect.speed_mod

        all_units = [(m, "party") for m in party_members if m.hp > 0] + \
                    [(e, "enemy") for e in enemies if e.hp > 0]
        all_units.sort(key=lambda x: x[0].speed * (final_spd_mod if x[1] == "party" else 1.0), reverse=True)

        for unit, side in all_units:
            if unit.hp <= 0: continue

            if side == "party":
                targets = [e for e in enemies if e.hp > 0]
                if not targets: break

                if priority == AIPriority.WOUNDED:
                    target = min(targets, key=lambda x: x.hp)
                else:
                    target = random.choice(targets)

                attacker_name, defender_name = unit.name, target.name

                # Skill activation
                dmg_mult = 1.0
                for skill in unit.skills:
                    if skill.name == "Power Strike" and random.random() < 0.25:
                        dmg_mult = 1.7
                        log.append(f"{attacker_name} unleashes POWER STRIKE!")
                    elif skill.name == "Quick Shot" and random.random() < 0.3:
                        dmg_mult = 1.3
                        log.append(f"{attacker_name} performs a QUICK SHOT!")

                # Accuracy check
                if random.randint(1, 100) > unit.effective_accuracy:
                    log.append(f"{attacker_name} misses {defender_name}!")
                    continue

                atk = unit.effective_attack * final_atk_mod

                # Crit check
                if random.randint(1, 100) <= unit.critical_chance:
                    dmg_mult *= 1.5
                    log.append("CRITICAL HIT!")

                dfn = target.defense
            else:
                targets = [m for m in party_members if m.hp > 0]
                if not targets: break
                target = random.choice(targets)
                attacker_name, defender_name = "Enemy " + unit.name, target.name
                atk = unit.attack
                dmg_mult = 1.0
                dfn = target.effective_defense * final_def_mod

            damage = max(1, int((atk - (dfn // 2)) * dmg_mult))
            target.hp = max(0, target.hp - damage)
            log.append(f"{attacker_name} attacks {defender_name} for {damage} damage!")

            if target.hp <= 0:
                log.append(f"{defender_name} falls!")
                if side == "enemy":
                    CombatSimulator._check_for_injury(target, log)

        return {"log": log}

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
            msg = f"SEVERE: {character.name} sustained an injury: {injury.name}!"
            log.append(msg)
            character.combat_log.append(msg)

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
