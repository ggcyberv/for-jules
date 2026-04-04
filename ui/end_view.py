import pygame
from typing import Optional
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE

class EndView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.SysFont("Arial", 24)
        self.large_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.button_rect = pygame.Rect(self.width // 2 - 100, 450, 200, 50)

    def render(self, screen: pygame.Surface, victory: bool, turns: int):
        screen.fill((10, 10, 15))

        # Result Title
        color = COLOR_TEXT_GOLD if victory else (200, 50, 50)
        text = "GLORIOUS VICTORY" if victory else "PARTY WIPED OUT"
        title_surf = self.large_font.render(text, True, color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 200))
        screen.blit(title_surf, title_rect)

        # Stats
        stat_text = f"Your journey lasted {turns} turns."
        s_surf = self.font.render(stat_text, True, COLOR_TEXT_WHITE)
        s_rect = s_surf.get_rect(center=(self.width // 2, 300))
        screen.blit(s_surf, s_rect)

        # Menu Button
        mx, my = pygame.mouse.get_pos()
        UIHelper.draw_button(screen, self.button_rect, "Main Menu", self.font, self.button_rect.collidepoint(mx, my))

    def handle_click(self, pos) -> bool:
        return self.button_rect.collidepoint(pos)
