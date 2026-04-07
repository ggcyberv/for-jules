import pygame
from typing import List, Optional
from party.party_manager import Party
from party.character import Character
from party.item import Item
from engine.game_state import GameState
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_FRAME_GOLD, COLOR_HP_RED, COLOR_XP_GREEN, COLOR_BUTTON_NORMAL

class PartyView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 750
        self.height = 550
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 12)
        self.large_font = pygame.font.SysFont("Arial", 22)
        self.char_idx = 0
        self.tab = "party" # "party", "lore", "logs"
        self.attr_rects = []

    def render(self, screen: pygame.Surface, party: Party):
        UIHelper.draw_frame(screen, self.rect)

        cat_tabs = ["Party", "Journal", "Lore & Secrets", "Combat History", "World History"]
        mx, my = pygame.mouse.get_pos()
        for i, cat in enumerate(cat_tabs):
            tab_id = cat.lower().split()[0]
            t_rect = pygame.Rect(self.rect.x + 20 + i * 140, self.rect.y - 30, 130, 30)
            is_hovered = t_rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, t_rect, cat, self.small_font, is_hovered or self.tab == tab_id)

        if self.tab == "party":
            self._render_party(screen, party)
        elif self.tab == "lore":
            self._render_lore(screen)
        elif self.tab == "combat":
            self._render_logs(screen, party)
        elif self.tab == "world":
            self._render_world_history(screen)
        elif self.tab == "journal":
            self._render_journal(screen)

    def _render_party(self, screen, party):
        mx, my = pygame.mouse.get_pos()
        for i, char in enumerate(party.members):
            tab_rect = pygame.Rect(self.rect.x + 20 + i * 110, self.rect.y + 20, 100, 30)
            is_active = (i == self.char_idx)
            is_hovered = tab_rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, tab_rect, char.name, self.small_font, is_hovered or is_active)

        if not party.members: return
        char = party.members[self.char_idx]

        detail_y = self.rect.y + 70
        title_surf = self.large_font.render(f"{char.name} - Level {char.level}", True, COLOR_TEXT_GOLD)
        screen.blit(title_surf, (self.rect.x + 20, detail_y))

        # XP Bar
        xp_text = f"XP: {char.xp} / {char.xp_required}"
        xp_surf = self.small_font.render(xp_text, True, COLOR_TEXT_WHITE)
        screen.blit(xp_surf, (self.rect.x + 20, detail_y + 35))
        UIHelper.draw_progress_bar(screen, self.rect.x + 20, detail_y + 55, 250, 10, char.xp, char.xp_required, COLOR_XP_GREEN)

        # Stats Display Refactored
        stat_y = detail_y + 80
        if char.attribute_points > 0:
            ap_surf = self.font.render(f"Attribute Points: {char.attribute_points}", True, COLOR_TEXT_GOLD)
            screen.blit(ap_surf, (self.rect.x + 20, stat_y))
            stat_y += 30

        base_stats = [
            ("STR", char.str, "base_str"), ("AGI", char.agi, "base_agi"),
            ("CON", char.con, "base_con"), ("PER", char.per, "base_per"),
            ("INT", char.int, "base_int"), ("CHA", char.cha, "base_cha")
        ]

        self.attr_rects = []
        for name, val, key in base_stats:
            text = f"{name}: {val}"
            surf = self.font.render(text, True, COLOR_TEXT_WHITE)
            screen.blit(surf, (self.rect.x + 20, stat_y))
            if char.attribute_points > 0:
                plus_rect = pygame.Rect(self.rect.x + 100, stat_y, 20, 20)
                UIHelper.draw_button(screen, plus_rect, "+", self.small_font, plus_rect.collidepoint(mx, my))
                self.attr_rects.append((plus_rect, key))
            stat_y += 25

        stat_y += 10
        derived_stats = [
            ("Phys Atk", f"{char.phys_atk:.1f}"),
            ("Mag Atk", f"{char.mag_atk:.1f}"),
            ("Armor", f"{char.armor_val:.1f}"),
            ("Dodge", f"{char.dodge_chance*100:.1f}%"),
            ("Crit", f"{char.crit_chance*100:.1f}%")
        ]
        for name, val in derived_stats:
            text = f"{name}: {val}"
            surf = self.font.render(text, True, (200, 200, 200))
            screen.blit(surf, (self.rect.x + 140, detail_y + 110 + (derived_stats.index((name, val)) * 25)))

        # Character Info (Race/Age/Size)
        info_text = f"{char.race} | {char.age_category} | {char.size} | {char.backstory_name}"
        info_surf = self.small_font.render(info_text, True, (150, 150, 150))
        screen.blit(info_surf, (self.rect.x + 20, detail_y + 20))

        mid_x = self.rect.x + 300
        bs_title = self.font.render("Backstory:", True, (200, 200, 255))
        screen.blit(bs_title, (mid_x, detail_y))
        words = char.backstory.split()
        lines = []; curr = ""
        for w in words:
            if self.small_font.size(curr + w + " ")[0] < 200: curr += w + " "
            else: lines.append(curr); curr = w + " "
        lines.append(curr)
        for i, l in enumerate(lines[:5]):
            surf = self.small_font.render(l, True, (200, 200, 200)); screen.blit(surf, (mid_x, detail_y + 30 + i * 15))

        skill_y = detail_y + 130
        sk_title = self.font.render("Skills:", True, (200, 200, 255))
        screen.blit(sk_title, (mid_x, skill_y))
        for i, skill in enumerate(char.skills[:4]):
            surf = self.small_font.render(f"{skill.name}: {skill.description}", True, (220, 220, 220))
            screen.blit(surf, (mid_x, skill_y + 30 + i * 20))

        rel_y = skill_y + 110
        rel_title = self.font.render("Relationships:", True, (200, 200, 255))
        screen.blit(rel_title, (mid_x, rel_y))
        for i, (name, score) in enumerate(char.relationships.items()):
            status = "Friendly" if score > 10 else ("Cold" if score < -10 else "Neutral")
            surf = self.small_font.render(f"{name}: {score} ({status})", True, (220, 220, 220))
            screen.blit(surf, (mid_x, rel_y + 30 + i * 20))

        eq_x = self.rect.x + 520
        eq_title = self.font.render("Equipment:", True, (200, 200, 255))
        screen.blit(eq_title, (eq_x, detail_y))

        # 9 Slots Layout (Ring x2, Shield)
        from party.item import Weapon, Armor, Shield, Item as GearItem
        eq_slots = [
            ("Weapon", char.equipment.main_hand, "main_hand"),
            ("Armor", char.equipment.body, "body"),
            ("Shield", char.equipment.shield, "shield"),
            ("Helm", char.equipment.helm, "helm"),
            ("Gloves", char.equipment.gloves, "gloves"),
            ("Boots", char.equipment.boots, "boots"),
            ("Amulet", char.equipment.amulet, "amulet"),
            ("Ring 1", char.equipment.ring1, "ring1"),
            ("Ring 2", char.equipment.ring2, "ring2")
        ]

        self.eq_rects = []
        for i, (label, item, key) in enumerate(eq_slots):
            col = i // 5
            row = i % 5
            sx = eq_x + col * 120
            sy = detail_y + 30 + row * 45

            item_name = item.display_name if item else "None"
            color = item.rarity.color if item else (150, 150, 150)

            surf = self.small_font.render(f"{label}:", True, (150, 150, 150))
            screen.blit(surf, (sx, sy))

            name_surf = self.small_font.render(item_name, True, color)
            name_rect = name_surf.get_rect(topleft=(sx, sy + 15))
            screen.blit(name_surf, name_rect)

            # Store rect for hit detection (tooltips handled below)
            hit_rect = pygame.Rect(sx, sy, 110, 40)
            self.eq_rects.append((hit_rect, item))

        inv_y = self.rect.y + 380
        inv_title = self.font.render(f"Party Inventory (Gold: {party.gold}, Food: {party.food}):", True, (200, 255, 200))
        screen.blit(inv_title, (self.rect.x + 20, inv_y))
        self.inv_rects = []
        for i, item in enumerate(party.inventory[:12]):
            ix = self.rect.x + 20 + (i % 3) * 230; iy = inv_y + 30 + (i // 3) * 20
            i_rect = pygame.Rect(ix, iy, 200, 20)
            is_hovered = i_rect.collidepoint(mx, my)

            if isinstance(item, GearItem):
                text = f"- {item.display_name} (Lvl {item.item_level})"
                color = item.rarity.color
            else:
                text = f"- {str(item)}"
                color = (200, 200, 200)

            if is_hovered: color = COLOR_TEXT_GOLD
            screen.blit(self.small_font.render(text, True, color), (ix, iy))
            self.inv_rects.append((i_rect, i))

        # Tooltips layer (render last to overlap)
        for rect, item in self.eq_rects:
            if rect.collidepoint(mx, my) and item:
                self._render_item_tooltip(screen, mx, my, item)
        for i_rect, idx in self.inv_rects:
            if i_rect.collidepoint(mx, my) and idx < len(party.inventory):
                item = party.inventory[idx]
                if isinstance(item, GearItem):
                    self._render_item_tooltip(screen, mx, my, item)

        footer = "1-6: Switch | TAB: Tabs | ESC/I: Close"
        f_surf = self.small_font.render(footer, True, (150, 150, 150)); screen.blit(f_surf, (self.rect.x + 20, self.rect.bottom - 30))

    def _render_lore(self, screen):
        state = GameState()
        title = self.large_font.render("Lore & Discovered Secrets", True, (255, 215, 0))
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))
        y = self.rect.y + 70
        if not state.lore_manager.discovered_fragments:
            surf = self.font.render("No lore fragments discovered yet.", True, (150, 150, 150)); screen.blit(surf, (self.rect.x + 20, y))
        else:
            for frag in state.lore_manager.discovered_fragments:
                f_title = self.font.render(frag.title, True, (200, 200, 255)); screen.blit(f_title, (self.rect.x + 20, y)); y += 25
                f_content = self.small_font.render(frag.content, True, (220, 220, 220)); screen.blit(f_content, (self.rect.x + 40, y)); y += 30

    def _render_world_history(self, screen):
        state = GameState()
        title = self.large_font.render("World History & Faction Relations", True, COLOR_TEXT_GOLD)
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))

        # History
        y = self.rect.y + 70
        h_title = self.font.render("History:", True, (200, 200, 255))
        screen.blit(h_title, (self.rect.x + 20, y))
        y += 30
        if not state.world_facts:
            surf = self.font.render("The history of this realm is yet to be written.", True, (150, 150, 150))
            screen.blit(surf, (self.rect.x + 40, y))
            y += 40
        else:
            for fact in state.world_facts[-5:]:
                f_text = f"Turn {fact.turn_recorded}: {fact.description}"
                y += UIHelper.render_text_wrapped(screen, f_text, (self.rect.x + 40, y), self.small_font, self.width // 2 - 60)
                y += 5

        # Faction Relations
        ry = self.rect.y + 70
        rx = self.rect.x + self.width // 2
        r_title = self.font.render("Faction Diplomacy:", True, (200, 200, 255))
        screen.blit(r_title, (rx, ry))
        ry += 30
        for pair, score in state.faction_system.relations.items():
            status = "War" if score <= -50 else ("Allied" if score >= 50 else "Neutral")
            f1, f2 = pair
            rel_text = f"{f1.capitalize()} - {f2.capitalize()}: {score} ({status})"
            screen.blit(self.small_font.render(rel_text, True, (220, 220, 220)), (rx + 20, ry))
            ry += 20

    def _render_journal(self, screen):
        state = GameState()
        title = self.large_font.render("Quest Journal", True, COLOR_TEXT_GOLD)
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))
        y = self.rect.y + 70

        active = [q for q in state.quest_manager.quests.values() if q.is_active and not q.is_finished]
        finished = [q for q in state.quest_manager.quests.values() if q.is_finished]

        # Active Quests
        a_title = self.font.render("Active Quests:", True, (200, 200, 255))
        screen.blit(a_title, (self.rect.x + 20, y))
        y += 30
        if not active:
            screen.blit(self.small_font.render("No active quests.", True, (150, 150, 150)), (self.rect.x + 40, y))
            y += 30
        else:
            for q in active:
                screen.blit(self.font.render(q.title, True, COLOR_TEXT_WHITE), (self.rect.x + 40, y))
                y += 20
                y += UIHelper.render_text_wrapped(screen, q.description, (self.rect.x + 60, y), self.small_font, self.width - 100)
                y += 10

        # Finished Quests
        y += 20
        f_title = self.font.render("Completed Quests:", True, (200, 255, 200))
        screen.blit(f_title, (self.rect.x + 20, y))
        y += 30
        for q in finished:
            screen.blit(self.small_font.render(f"- {q.title}", True, (200, 200, 200)), (self.rect.x + 40, y))
            y += 20

    def _render_logs(self, screen, party):
        char = party.members[self.char_idx] if party.members else None
        title = self.large_font.render(f"Combat History: {char.name if char else ''}", True, (255, 215, 0))
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))
        y = self.rect.y + 70
        if not char or not char.combat_log:
            surf = self.font.render("No combat entries yet.", True, (150, 150, 150)); screen.blit(surf, (self.rect.x + 20, y))
        else:
            for entry in char.combat_log[-12:]:
                lsurf = self.small_font.render(f"> {entry}", True, (200, 200, 200))
                screen.blit(lsurf, (self.rect.x + 20, y))
                y += 20

    def handle_keydown(self, key, party: Party):
        if key == pygame.K_TAB:
            tabs = ["party", "journal", "lore", "combat", "world"]
            self.tab = tabs[(tabs.index(self.tab) + 1) % len(tabs)]
        elif self.tab in ["party", "combat"]:
            new_idx = -1
            if key == pygame.K_1: new_idx = 0
            elif key == pygame.K_2: new_idx = 1
            elif key == pygame.K_3: new_idx = 2
            elif key == pygame.K_4: new_idx = 3
            elif key == pygame.K_5: new_idx = 4
            elif key == pygame.K_6: new_idx = 5

            if new_idx != -1 and new_idx < len(party.members):
                self.char_idx = new_idx

    def _render_item_tooltip(self, screen, x, y, item):
        from party.item import Weapon, Armor
        lines = [f"{item.display_name} ({item.rarity.label})", f"Level {item.item_level} {item.slot.name.lower().capitalize()}"]

        if isinstance(item, Weapon):
            lines.append(f"Damage: {item.base_dmg_min}-{item.base_dmg_max}")
            for stat, scale in item.scaling.items():
                lines.append(f"Scaling: {int(scale*100)}% {stat}")
            for prop, val in item.properties.items():
                lines.append(f"{prop.replace('_', ' ').capitalize()}: {val}")
        elif isinstance(item, Armor):
            lines.append(f"Armor: {item.base_armor}")
            if item.speed_penalty: lines.append(f"Speed Penalty: {item.speed_penalty}")
            if item.dodge_penalty: lines.append(f"Dodge Penalty: {int(item.dodge_penalty*100)}%")
            for eff, val in item.bonus_effects.items():
                lines.append(f"{eff.capitalize()}: {val}")

        for affix in item.affixes:
            sign = "+" if affix.value > 0 else ""
            val_str = f"{sign}{affix.value:.1f}%" if affix.is_percent else f"{sign}{int(affix.value)}"
            lines.append(f"{affix.name}: {val_str} {affix.stat}")

        padding = 10
        line_surfs = [self.small_font.render(l, True, (255, 255, 255)) for l in lines]
        width = max(s.get_width() for s in line_surfs) + padding * 2
        height = sum(s.get_height() + 2 for s in line_surfs) + padding * 2

        rect = pygame.Rect(x + 15, y, width, height)
        if rect.right > self.width + self.rect.x: rect.right = x - 15

        pygame.draw.rect(screen, (20, 20, 30), rect)
        pygame.draw.rect(screen, item.rarity.color, rect, 1)

        curr_y = rect.y + padding
        for surf in line_surfs:
            screen.blit(surf, (rect.x + padding, curr_y))
            curr_y += surf.get_height() + 2

    def handle_click(self, pos, party: Party) -> bool:
        if self.tab != "party" or not party.members: return False
        char = party.members[self.char_idx]

        # Equipment logic
        from party.item import Weapon, Armor, Shield, EquipSlot, Item as GearItem
        for i_rect, idx in getattr(self, 'inv_rects', []):
            if i_rect.collidepoint(pos) and idx < len(party.inventory):
                item = party.inventory[idx]
                if not isinstance(item, GearItem): continue

                # Determine target slot
                slot_key = None
                if item.slot == EquipSlot.WEAPON: slot_key = "main_hand"
                elif item.slot == EquipSlot.ARMOR: slot_key = "body"
                elif item.slot == EquipSlot.SHIELD: slot_key = "shield"
                elif item.slot == EquipSlot.HELM: slot_key = "helm"
                elif item.slot == EquipSlot.GLOVES: slot_key = "gloves"
                elif item.slot == EquipSlot.BOOTS: slot_key = "boots"
                elif item.slot == EquipSlot.AMULET: slot_key = "amulet"
                elif item.slot == EquipSlot.RING:
                    if char.equipment.ring1 is None: slot_key = "ring1"
                    elif char.equipment.ring2 is None: slot_key = "ring2"
                    else: slot_key = "ring1"

                if slot_key:
                    old = getattr(char.equipment, slot_key)
                    setattr(char.equipment, slot_key, item)
                    if old:
                        party.inventory[idx] = old
                    else:
                        party.inventory.pop(idx)
                    return True

        for rect, attr in self.attr_rects:
            if rect.collidepoint(pos) and char.attribute_points > 0:
                setattr(char, attr, getattr(char, attr) + 1)
                char.attribute_points -= 1
                return True
        return False
