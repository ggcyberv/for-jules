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

    def render(self, screen: pygame.Surface, enemies: List[Character], current_tactic: TacticType, current_formation: FormationType):
        UIHelper.draw_frame(screen, self.rect)

        # Enemies Info
        y = self.rect.y + 20
        title = self.large_font.render("ENEMIES SPOTTED!", True, (255, 50, 50))
        screen.blit(title, (self.rect.x + 20, y))
        y += 40
        for e in enemies:
            screen.blit(self.font.render(f"- {e.name} (HP: {e.hp})", True, COLOR_TEXT_WHITE), (self.rect.x + 40, y))
            y += 25

        # Tactical Settings
        y = self.rect.y + 150
        screen.blit(self.large_font.render("Tactical Preparation:", True, COLOR_TEXT_GOLD), (self.rect.x + 20, y))
        y += 40

        self.button_rects = []
        mx, my = pygame.mouse.get_pos()

        # Tactic Button
        t_rect = pygame.Rect(self.rect.x + 40, y, 200, 35)
        UIHelper.draw_button(screen, t_rect, f"Tactic: {current_tactic.value}", self.font, t_rect.collidepoint(mx, my))
        self.button_rects.append((t_rect, "cycle_tactic"))

        # Formation Button
        f_rect = pygame.Rect(self.rect.x + 40, y + 50, 200, 35)
        UIHelper.draw_button(screen, f_rect, f"Formation: {current_formation.value}", self.font, f_rect.collidepoint(mx, my))
        self.button_rects.append((f_rect, "cycle_formation"))

        # Start Battle Button
        s_rect = pygame.Rect(self.rect.centerx - 100, self.rect.bottom - 60, 200, 40)
        UIHelper.draw_button(screen, s_rect, "BEGIN BATTLE", self.large_font, s_rect.collidepoint(mx, my))
        self.button_rects.append((s_rect, "start"))

    def handle_click(self, pos) -> Optional[str]:
        for rect, action in self.button_rects:
            if rect.collidepoint(pos):
                return action
        return None
