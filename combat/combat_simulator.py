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
                race = data.get("race", "Human")
                backstory = data.get("backstory", "Soldier")
                c = Character(
                    name=data["name"],
                    race=race,
                    backstory_name=backstory,
                    level=data.get("level", 1),
                    base_str=data.get("STR", 10),
                    base_agi=data.get("AGI", 10),
                    base_con=data.get("CON", 10),
                    base_per=data.get("PER", 10),
                    base_int=data.get("INT", 10),
                    base_cha=data.get("CHA", 10)
                ).set_loot(data.get("loot_gold", 10))
                c.hp = c.max_hp
                c.mana = c.max_mana
                return c
        return Character("Unknown", race="Human", backstory_name="Soldier").set_loot(10)

    @staticmethod
    def simulate_battle(party_members: List[Character],
                        enemies: List[Character],
                        formation: FormationType = FormationType.NONE) -> Dict[str, Any]:
        log = []
        round_num = 1
        while any(m.hp > 0 for m in party_members) and any(e.hp > 0 for e in enemies) and round_num <= 20:
            round_res = CombatSimulator.simulate_round(party_members, enemies, round_num, formation)
            log.extend(round_res["log"])
            round_num += 1

        victory = any(m.hp > 0 for m in party_members) and not any(e.hp > 0 for e in enemies)
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
                       formation: FormationType = FormationType.NONE) -> Dict[str, Any]:
        log = [f"Round {round_num}"]
        f_effect = FORMATION_EFFECTS[formation]

        all_units = [(m, "party") for m in party_members if m.hp > 0] + \
                    [(e, "enemy") for e in enemies if e.hp > 0]

        # Determine action speed per unit
        def get_speed(u):
            return u.action_speed * f_effect.speed_mod

        all_units.sort(key=lambda x: get_speed(x[0]), reverse=True)

        for unit, side in all_units:
            if unit.hp <= 0: continue

            # Status: Stun check
            if hasattr(unit, 'status_effects') and "stun" in unit.status_effects:
                log.append(f"{unit.name} is stunned and skips their turn!")
                # Decrease stun duration/remove
                if isinstance(unit.status_effects["stun"], int):
                    unit.status_effects["stun"] -= 1
                    if unit.status_effects["stun"] <= 0:
                        del unit.status_effects["stun"]
                else:
                    del unit.status_effects["stun"]
                continue

            # Morale Check
            if unit.morale < 15 and random.random() < 0.4:
                log.append(f"{unit.name}'s morale breaks! They flee from the frontlines!")
                unit.hp = 0 # Simplified 'fleeing' as out of combat
                continue

            if side == "party":
                # Check for healing intervention based on individual threshold
                if unit.hp < (unit.max_hp * unit.heal_threshold / 100):
                    # Check if hero has a heal skill (mocked for now, or just self-heal)
                    heal_amt = 15
                    unit.hp = min(unit.max_hp, unit.hp + heal_amt)
                    log.append(f"{unit.name} prioritizes healing! Restored {heal_amt} HP.")
                    continue

                targets = [e for e in enemies if e.hp > 0]
                if not targets: break

                # Priority logic
                if unit.combat_priority == AIPriority.WOUNDED.value:
                    target = min(targets, key=lambda x: x.hp)
                elif unit.combat_priority == AIPriority.HEALERS.value:
                    healers = [e for e in targets if "healer" in e.name.lower() or "shaman" in e.name.lower()]
                    target = random.choice(healers) if healers else random.choice(targets)
                elif unit.combat_priority == AIPriority.CASTER.value:
                    casters = [e for e in targets if "mage" in e.name.lower() or "warlock" in e.name.lower()]
                    target = random.choice(casters) if casters else random.choice(targets)
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

                # Accuracy vs Dodge
                accuracy_mod = 0
                if unit.equipment.main_hand and "accuracy" in unit.equipment.main_hand.properties:
                    accuracy_mod = unit.equipment.main_hand.properties["accuracy"]

                # Sword property: reduces dodge by 5% (accuracy bonus)
                if random.random() < max(0, target.dodge_chance - accuracy_mod):
                    log.append(f"{defender_name} dodges the attack from {attacker_name}!")
                    continue

                t_effect = TACTIC_EFFECTS[TacticType(unit.combat_tactic)]

                # Reach Property (Spear)
                if unit.equipment.main_hand and "reach" in unit.equipment.main_hand.properties:
                    # Logic for rows could be added here if positions were implemented
                    pass

                # Armor Penetration
                armor_pen = 0
                if unit.equipment.main_hand and "armor_pen" in unit.equipment.main_hand.properties:
                    armor_pen = unit.equipment.main_hand.properties["armor_pen"]

                atk = unit.phys_atk * t_effect.attack_mod * f_effect.attack_mod

                # Crit check
                if random.random() <= unit.crit_chance:
                    dmg_mult *= unit.crit_damage
                    log.append("CRITICAL HIT!")

                dfn_val = target.armor_val * (1.0 - armor_pen)
            else:
                targets = [m for m in party_members if m.hp > 0]
                if not targets: break
                target = random.choice(targets)
                attacker_name, defender_name = "Enemy " + unit.name, target.name

                # Dodge check for party member
                if random.random() < target.dodge_chance:
                    log.append(f"{defender_name} dodges the attack from {attacker_name}!")
                    continue

                # NPC Attack (Uses the same stat system)
                atk = unit.phys_atk
                dmg_mult = 1.0

                # Find target's formation/tactic defense mods
                t_target_effect = TACTIC_EFFECTS[TacticType(target.combat_tactic)]
                dfn_val = target.armor_val * t_target_effect.defense_mod * f_effect.defense_mod

            # Block Chance (Shield)
            if target.equipment.shield:
                if random.random() < target.equipment.shield.block_chance:
                    dmg_mult *= 0.5
                    log.append(f"{defender_name} BLOCKS with their shield! (50% reduction)")

            # Armor reduction formula: Damage reduction = Armor / (Armor + 200)
            reduction_pct = dfn_val / (dfn_val + 200)
            pre_mitigation = int(atk * dmg_mult)
            damage = int(pre_mitigation * (1.0 - reduction_pct))
            damage = max(1, damage)

            target.hp = max(0, target.hp - damage)
            reduction = pre_mitigation - damage
            log.append(f"{attacker_name} attacks {defender_name} for {damage} dmg! ({pre_mitigation} base, -{reduction} armor)")

            # Apply Status Effects on certain conditions
            if not hasattr(target, 'status_effects'): target.status_effects = {}

            # Mace property: 10% stun
            if unit.equipment.main_hand and "stun_chance" in unit.equipment.main_hand.properties:
                if random.random() < unit.equipment.main_hand.properties["stun_chance"]:
                    target.status_effects["stun"] = 1
                    log.append(f"{target.name} is STUNNED by the heavy blow!")

            if "Skeleton" in attacker_name and random.random() < 0.2:
                target.status_effects["stun"] = 1
                log.append(f"{target.name} is STUNNED by the bone-crushing blow!")

            # Morale Reduction on damage
            if damage > 15:
                target.morale = max(0, target.morale - 5)

            if target.hp <= 0:
                log.append(f"{defender_name} falls!")
                # Significant morale loss for allies of the fallen
                target_side = "enemy" if side == "party" else "party"
                for u, s in all_units:
                    if s == target_side:
                        u.morale = max(0, u.morale - 15)

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
        # Check if action is a skill name
        for hero in party_members:
            if hero.hp > 0:
                for skill in hero.skills:
                    if skill.name.lower() == action_type.lower():
                        target_list = [e for e in enemies if e.hp > 0]
                        if target_list:
                            target = random.choice(target_list)
                            dmg = int(hero.effective_attack * 1.5)
                            target.hp = max(0, target.hp - dmg)
                            log.append(f"{hero.name} uses {skill.name}! Hits {target.name} for {dmg} damage!")
                            return log

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
        elif action_type == "taunt":
            for m in party_members:
                if m.hp > 0:
                    m.defense += 5
                    m.morale = min(m.max_morale, m.morale + 10)
            log.append("Divine intervention: Party morale restored and defense fortified!")
        elif action_type == "focus":
            for m in party_members:
                if m.hp > 0:
                    m.accuracy += 15
                    m.critical_chance += 10
            log.append("Divine intervention: Party accuracy and crit chance surged!")
        return log
