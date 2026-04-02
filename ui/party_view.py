import pygame
from typing import List, Optional
from party.party_manager import Party
from party.character import Character
from party.item import Item
from engine.game_state import GameState

class PartyView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 750
        self.height = 550
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 12)
        self.large_font = pygame.font.SysFont("Arial", 22)
        self.char_idx = 0
        self.tab = "party" # "party", "lore"
        self.attr_rects = []

    def render(self, screen: pygame.Surface, party: Party):
        pygame.draw.rect(screen, (30, 40, 50), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        # Tab headers (Main Categories)
        cat_tabs = ["Party", "Lore & Secrets"]
        for i, cat in enumerate(cat_tabs):
            t_rect = pygame.Rect(self.rect.x + 20 + i * 130, self.rect.y - 30, 120, 30)
            t_color = (100, 120, 140) if self.tab == cat.lower().split()[0] else (40, 50, 60)
            pygame.draw.rect(screen, t_color, t_rect)
            pygame.draw.rect(screen, (255, 255, 255), t_rect, 1)
            t_surf = self.font.render(cat, True, (255, 255, 255))
            screen.blit(t_surf, (t_rect.x + 10, t_rect.y + 5))

        if self.tab == "party":
            self._render_party(screen, party)
        else:
            self._render_lore(screen)

    def _render_party(self, screen, party):
        for i, char in enumerate(party.members):
            tab_rect = pygame.Rect(self.rect.x + 20 + i * 110, self.rect.y + 20, 100, 30)
            color = (100, 120, 140) if i == self.char_idx else (60, 70, 80)
            pygame.draw.rect(screen, color, tab_rect)
            pygame.draw.rect(screen, (255, 255, 255), tab_rect, 1)
            name_surf = self.small_font.render(char.name, True, (255, 255, 255))
            screen.blit(name_surf, (tab_rect.x + 5, tab_rect.y + 7))

        if not party.members: return
        char = party.members[self.char_idx]

        detail_y = self.rect.y + 70
        title_surf = self.large_font.render(f"{char.name} (Level {char.level})", True, (255, 215, 0))
        screen.blit(title_surf, (self.rect.x + 20, detail_y))

        stats = [("Attack", char.attack, char.effective_attack), ("Defense", char.defense, char.effective_defense), ("Speed", char.speed, char.effective_speed)]
        self.attr_rects = []
        for i, (name, base, eff) in enumerate(stats):
            text = f"{name}: {eff} (Base: {base})"
            surf = self.font.render(text, True, (255, 255, 255))
            screen.blit(surf, (self.rect.x + 20, detail_y + 40 + i * 30))
            if char.attribute_points > 0:
                plus_rect = pygame.Rect(self.rect.x + 250, detail_y + 40 + i * 30, 20, 20)
                pygame.draw.rect(screen, (0, 150, 0), plus_rect)
                self.attr_rects.append((plus_rect, name.lower()))

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
            surf = self.small_font.render(l, True, (200, 200, 200))
            screen.blit(surf, (mid_x, detail_y + 30 + i * 15))

        skill_y = detail_y + 120
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

        inv_y = self.rect.y + 350
        inv_title = self.font.render(f"Party Inventory (Gold: {party.gold}, Food: {party.food}):", True, (200, 255, 200))
        screen.blit(inv_title, (self.rect.x + 20, inv_y))
        for i, item in enumerate(party.inventory[:12]):
            ix = self.rect.x + 20 + (i % 3) * 230; iy = inv_y + 30 + (i // 3) * 20
            surf = self.small_font.render(f"- {str(item.name if hasattr(item, 'name') else item)}", True, (200, 200, 200)); screen.blit(surf, (ix, iy))

        footer = "1-6: Switch | S: Save | L: Load | TAB: Lore | ESC/I: Close"
        f_surf = self.small_font.render(footer, True, (150, 150, 150)); screen.blit(f_surf, (self.rect.x + 20, self.rect.bottom - 30))

    def _render_lore(self, screen):
        state = GameState()
        title = self.large_font.render("Lore & Discovered Secrets", True, (255, 215, 0))
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))

        y = self.rect.y + 70
        if not state.lore_manager.discovered_fragments:
            surf = self.font.render("No lore fragments discovered yet.", True, (150, 150, 150))
            screen.blit(surf, (self.rect.x + 20, y))
        else:
            for frag in state.lore_manager.discovered_fragments:
                f_title = self.font.render(frag.title, True, (200, 200, 255))
                screen.blit(f_title, (self.rect.x + 20, y))
                y += 25
                f_content = self.small_font.render(frag.content, True, (220, 220, 220))
                screen.blit(f_content, (self.rect.x + 40, y))
                y += 30

    def handle_keydown(self, key):
        if key == pygame.K_TAB:
            self.tab = "lore" if self.tab == "party" else "party"
        elif self.tab == "party":
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
