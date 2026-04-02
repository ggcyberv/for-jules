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

        cat_tabs = ["Party", "Lore & Secrets", "Combat History"]
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

        stats = [
            ("Attack", char.attack, char.effective_attack),
            ("Defense", char.defense, char.effective_defense),
            ("Speed", char.speed, char.effective_speed),
            ("Accuracy", char.accuracy, char.effective_accuracy),
            ("Critical %", char.critical_chance, char.critical_chance)
        ]
        self.attr_rects = []
        stat_y = detail_y + 80
        if char.attribute_points > 0:
            ap_surf = self.font.render(f"Attribute Points: {char.attribute_points}", True, COLOR_TEXT_GOLD)
            screen.blit(ap_surf, (self.rect.x + 20, stat_y))
            stat_y += 30

        for i, (name, base, eff) in enumerate(stats):
            text = f"{name}: {eff}"
            surf = self.font.render(text, True, COLOR_TEXT_WHITE)
            screen.blit(surf, (self.rect.x + 20, stat_y))
            if char.attribute_points > 0 and i < 3: # Can only increase core stats
                plus_rect = pygame.Rect(self.rect.x + 250, stat_y, 20, 20)
                UIHelper.draw_button(screen, plus_rect, "+", self.small_font, plus_rect.collidepoint(mx, my))
                self.attr_rects.append((plus_rect, name.lower()))
            stat_y += 30

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
        for i, item in enumerate(party.inventory[:9]):
            ix = self.rect.x + 20 + (i % 3) * 230; iy = inv_y + 30 + (i // 3) * 20
            surf = self.small_font.render(f"- {str(item.name if hasattr(item, 'name') else item)}", True, (200, 200, 200)); screen.blit(surf, (ix, iy))

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
            tabs = ["party", "lore", "combat"]
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
        for rect, attr in self.attr_rects:
            if rect.collidepoint(pos) and char.attribute_points > 0:
                if attr == "attack": char.attack += 1
                elif attr == "defense": char.defense += 1
                elif attr == "speed": char.speed += 1
                char.attribute_points -= 1
                return True
        return False
