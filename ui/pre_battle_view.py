import pygame
from typing import List, Optional
from party.character import Character
from combat.tactics import TacticType, FormationType, AIPriority
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE

class PreBattleView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 600
        self.height = 400
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 16)
        self.large_font = pygame.font.SysFont("Arial", 22)
        self.button_rects: List[pygame.Rect] = []
        self.tactic_options = list(TacticType)
        self.formation_options = list(FormationType)

    def render(self, screen: pygame.Surface, party: List[Character], enemies: List[Character], current_formation: FormationType):
        UIHelper.draw_frame(screen, self.rect)
        mx, my = pygame.mouse.get_pos()
        self.button_rects = []

        # Enemies Info (Left Side)
        y = self.rect.y + 20
        title = self.large_font.render("ENEMIES", True, (255, 50, 50))
        screen.blit(title, (self.rect.x + 20, y))
        y += 40
        for e in enemies:
            screen.blit(self.font.render(f"- {e.name} (HP: {e.hp})", True, COLOR_TEXT_WHITE), (self.rect.x + 40, y))
            y += 25

        # Party Preparation (Right Side)
        y = self.rect.y + 20
        p_title = self.large_font.render("PARTY TACTICS", True, COLOR_TEXT_GOLD)
        screen.blit(p_title, (self.rect.x + 300, y))
        y += 40

        for i, hero in enumerate(party):
            h_y = y + i * 80
            screen.blit(self.medium_font.render(hero.name, True, COLOR_TEXT_WHITE), (self.rect.x + 300, h_y))

            # Tactic cycle
            t_rect = pygame.Rect(self.rect.x + 300, h_y + 20, 120, 25)
            UIHelper.draw_button(screen, t_rect, f"{hero.combat_tactic}", self.font, t_rect.collidepoint(mx, my))
            self.button_rects.append((t_rect, f"hero_{i}_tactic"))

            # Priority cycle
            p_rect = pygame.Rect(self.rect.x + 430, h_y + 20, 120, 25)
            UIHelper.draw_button(screen, p_rect, f"{hero.combat_priority}", self.font, p_rect.collidepoint(mx, my))
            self.button_rects.append((p_rect, f"hero_{i}_priority"))

            # Heal threshold cycle
            h_rect = pygame.Rect(self.rect.x + 300, h_y + 50, 250, 25)
            UIHelper.draw_button(screen, h_rect, f"Heal if HP < {hero.heal_threshold}%", self.font, h_rect.collidepoint(mx, my))
            self.button_rects.append((h_rect, f"hero_{i}_heal"))

        # Global Formation (Bottom Left)
        f_rect = pygame.Rect(self.rect.x + 20, self.rect.bottom - 110, 250, 35)
        UIHelper.draw_button(screen, f_rect, f"Formation: {current_formation.value}", self.font, f_rect.collidepoint(mx, my))
        self.button_rects.append((f_rect, "cycle_formation"))

        # Start Battle Button (Bottom Center)
        s_rect = pygame.Rect(self.rect.centerx - 100, self.rect.bottom - 60, 200, 40)
        UIHelper.draw_button(screen, s_rect, "BEGIN BATTLE", self.large_font, s_rect.collidepoint(mx, my))
        self.button_rects.append((s_rect, "start"))

    def handle_click(self, pos) -> Optional[str]:
        for rect, action in self.button_rects:
            if rect.collidepoint(pos):
                return action
        return None
