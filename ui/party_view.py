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
        xp_text = f"XP: {char.xp} / {char.level * 100}"
        xp_surf = self.small_font.render(xp_text, True, COLOR_TEXT_WHITE)
        screen.blit(xp_surf, (self.rect.x + 20, detail_y + 35))
        UIHelper.draw_progress_bar(screen, self.rect.x + 20, detail_y + 55, 250, 10, char.xp % (char.level * 100), char.level * 100, COLOR_XP_GREEN)

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
        eq_slots = [("Main Hand", char.equipment.main_hand), ("Body", char.equipment.body)]
        for i, (slot, item) in enumerate(eq_slots):
            item_name = item.name if item else "None"
            surf = self.font.render(f"{slot}:", True, (150, 150, 150)); screen.blit(surf, (eq_x, detail_y + 30 + i * 40))
            name_surf = self.small_font.render(item_name, True, (255, 255, 255)); screen.blit(name_surf, (eq_x, detail_y + 50 + i * 40))

        inv_y = self.rect.y + 380
        inv_title = self.font.render(f"Party Inventory (Gold: {party.gold}, Food: {party.food}):", True, (200, 255, 200))
        screen.blit(inv_title, (self.rect.x + 20, inv_y))
        self.inv_rects = []
        for i, item in enumerate(party.inventory[:9]):
            ix = self.rect.x + 20 + (i % 3) * 230; iy = inv_y + 30 + (i // 3) * 20
            i_rect = pygame.Rect(ix, iy, 200, 20)
            is_hovered = i_rect.collidepoint(mx, my)
            text = f"- {str(item.name if hasattr(item, 'name') else item)}"
            color = COLOR_TEXT_GOLD if is_hovered else (200, 200, 200)
            screen.blit(self.small_font.render(text, True, color), (ix, iy))
            self.inv_rects.append((i_rect, i))

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

    def handle_keydown(self, key):
        if key == pygame.K_TAB:
            tabs = ["party", "journal", "lore", "combat", "world"]
            self.tab = tabs[(tabs.index(self.tab) + 1) % len(tabs)]
        elif self.tab in ["party", "combat"]:
            if key == pygame.K_1: self.char_idx = 0
            elif key == pygame.K_2: self.char_idx = 1
            elif key == pygame.K_3: self.char_idx = 2
            elif key == pygame.K_4: self.char_idx = 3
            elif key == pygame.K_5: self.char_idx = 4
            elif key == pygame.K_6: self.char_idx = 5

    def handle_click(self, pos, party: Party) -> bool:
        if self.tab != "party" or not party.members: return False
        char = party.members[self.char_idx]

        # Equipment logic
        from party.item import Weapon, Armor
        for i_rect, idx in getattr(self, 'inv_rects', []):
            if i_rect.collidepoint(pos) and idx < len(party.inventory):
                item = party.inventory[idx]
                if isinstance(item, Weapon):
                    # Swap main hand
                    old = char.equipment.main_hand
                    char.equipment.main_hand = item
                    party.inventory[idx] = old if old else "Scrap Metal"
                    return True
                elif isinstance(item, Armor):
                    old = char.equipment.body
                    char.equipment.body = item
                    party.inventory[idx] = old if old else "Old Rags"
                    return True

        for rect, attr in self.attr_rects:
            if rect.collidepoint(pos) and char.attribute_points > 0:
                setattr(char, attr, getattr(char, attr) + 1)
                char.attribute_points -= 1
                return True
        return False
