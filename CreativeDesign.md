# Chronicles of the Unbound Realm: Creative & Systems Design Document

## 1. Creative Vision & World Identity
The Unbound Realm is a post-cataclysmic world where the boundaries of magic and reality have frayed. Civilizations have retreated to isolated city-states, and the vast wilderness between them is a shifting, dangerous "unbound" territory where ancient ruins and eldritch anomalies are common.

### 1.1 Core Biomes & Factions
| Biome | Predominant Faction | Narrative Theme | Key Dangers |
| :--- | :--- | :--- | :--- |
| **Plains of Echoes** | Northern Tribes / Nomads | Rebuilding after the "Sundering." | Bandit raiders, spiritual echoes. |
| **Whispering Forests** | Elven Remnants / Orc Tribes | Nature reclaimng the ruins of magic. | Dire wolves, sentient vines, ambushes. |
| **Jagged Spires** | Dwarven Outcasts / Dragons | High-altitude isolation and ancient technology. | Rocs, rock slides, extreme cold. |
| **The Rotting Lowlands** | Undead Legions / Necromancers | A blighted land where nothing truly stays dead. | Plague, skeletons, poison miasma. |

---

## 2. The Complex Interaction Matrix
The core of "Chronicles" is the interweaving of disparate systems into a single "Consequence Web."

### 2.1 The Consequence Web Architecture
Every significant action (Quest completion, Faction leader death, Choice in a random event) is logged as a **WorldFact** object.

**WorldFact Data Structure:**
- `fact_id`: Unique identifier (e.g., `bandit_king_slain`).
- `turn_recorded`: The turn number when it happened.
- `actors`: List of involved NPCs/Factions.
- `description`: Human-readable summary for the "Chronicle" log.
- `data`: Key-value pairs for system queries (e.g., `{"location": (12, 34), "method": "duel"}`).

### 2.2 System Intersections
| Trigger System | Impacted System | Interaction Logic |
| :--- | :--- | :--- |
| **Combat Outcome** | **NPCs / Factions** | If you spare a faction member in a duel (Event Choice), they become a "Blood Debt" NPC. Later, if you are captured, they may help you escape. |
| **Random Event** | **World Generation** | A choice to "Investigate the Rift" might spawn a permanent **Anomalous Dungeon** at your current hex coordinates via the `add_poi` consequence. |
| **Faction Relation** | **Player Choice** | Low reputation (-50) removes "Diplomatic" choices from events, forcing the player into "Bribe" or "Fight" outcomes. |
| **NPC Relationships** | **Combat Simulation** | High affinity between two party members triggers "Cover Action" where one unit takes damage for the other during the simulation. |

---

## 3. Dynamic Narrative & NPC AI
NPCs are not static; they are entities with their own goal-driven behaviors.

### 3.1 NPC Party Behaviors
- **Patrol:** Moves between two friendly towns, clearing nearby monster dens.
- **Chase:** Aggressively moves toward the player if faction reputation is Hostile.
- **Flee:** Moves away from the player if the NPC's power level is lower.
- **Trade:** Moves between markets, carrying rare inventory items that the player can buy if they meet them on the road.

### 3.2 Relationship Progression
Relationships (Affinity) change based on:
1. **Direct Choices:** Backing a member in a tavern brawl event (+10).
2. **Combat Shared Experience:** Every victory (+2), witnessing an injury (-5).
3. **Traits:** "Lone Wolf" members lose morale when the party is full.

---

## 4. Future Implementation Roadmap

### Milestone 2: The Living Faction System
- [ ] **Dynamic Territory Shift:** Factions capture adjacent neutral hexes over time.
- [ ] **Faction Missions:** Specific quests that directly affect world diplomacy (e.g., "Sabotage the Bandit Supply Line").
- [ ] **Bounty System:** Players with high negative reputation with a faction face "Bounty Hunter" NPC parties.

### Milestone 3: Advanced Narrative Integration
- [ ] **Event Chaining:** A WorldFact triggers a follow-up event 10-20 turns later (e.g., "The son of the merchant you robbed seeks vengeance").
- [ ] **Environmental Storytelling:** Hex tiles change visual appearance based on WorldFacts (e.g., a "Burned" forest after a dragon event).
- [ ] **Special Combat Interventions:** Unlock "Faction Ultimates" when Allied with a group (e.g., "Call in Nomad Skirmishers").

### Milestone 4: End-Game & Legacy
- [ ] **The Looming Threat:** A global countdown event (e.g., "The Void Opens") that unites or divides factions.
- [ ] **Legacy Saves:** Passing on "WorldFacts" to a new seed, creating a persistent history across multiple playthroughs.
