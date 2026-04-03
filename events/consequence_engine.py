from typing import Dict, Any, List
from engine.game_state import GameState

class ConsequenceEngine:
    @staticmethod
    def apply_consequence(outcome: Dict[str, Any]):
        state = GameState()

        if "add_flag" in outcome:
            state.global_flags[outcome["add_flag"]] = True

        if "modify_rep" in outcome:
            rep_data = outcome["modify_rep"]
            state.faction_system.adjust_reputation(rep_data["faction"], rep_data["amount"])

        if "faction_relation" in outcome:
            rel_data = outcome["faction_relation"]
            state.faction_system.adjust_faction_relation(rel_data["faction_a"], rel_data["faction_b"], rel_data["amount"])

        if "gold" in outcome:
            state.party.gold += outcome["gold"]

        if "food" in outcome:
            state.party.food += outcome["food"]

        if "log_fact" in outcome:
            fact_id = outcome["log_fact"]
            state.global_flags[f"fact_{fact_id}"] = {
                "turn": state.turn,
                "data": outcome.get("fact_data", {})
            }

        if "add_poi" in outcome:
            poi_data = outcome["add_poi"]
            from world.location import Dungeon
            poi_id = poi_data["id"]
            q, r = poi_data["q"], poi_data["r"]
            new_loc = Dungeon(poi_id=poi_id, name=poi_data["name"], q=q, r=r)
            state.locations[poi_id] = new_loc
            tile = state.world.get_tile(q, r)
            if tile:
                tile.poi_id = poi_id
                tile.discovered = True

        if "start_quest" in outcome:
            quest_id = outcome["start_quest"]
            state.quest_manager.start_quest(quest_id)

        if "update_quest" in outcome:
            update_data = outcome["update_quest"]
            state.quest_manager.update_objective(update_data["target"], update_data.get("amount", 1))

        if "world_fact" in outcome:
            from engine.game_state import WorldFact
            fact_data = outcome["world_fact"]
            new_fact = WorldFact(
                fact_id=fact_data["id"],
                turn_recorded=state.turn,
                actors=fact_data.get("actors", []),
                description=fact_data["description"],
                data=fact_data.get("extra", {})
            )
            state.world_facts.append(new_fact)
