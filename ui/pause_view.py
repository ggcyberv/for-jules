import pygame
from typing import Optional, List
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE

class PauseView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 300
        self.height = 350
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 20)
        self.options = ["Resume", "Save Game", "Load Game", "Main Menu"]
        self.button_rects = []

    def render(self, screen: pygame.Surface):
        # Dim background
        overlay = pygame.Surface((800, 600))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        screen.blit(overlay, (0, 0))

        UIHelper.draw_frame(screen, self.rect)

        y = self.rect.y + 40
        title = pygame.font.SysFont("Arial", 28, bold=True).render("PAUSED", True, COLOR_TEXT_GOLD)
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, y))

        self.button_rects = []
        y += 60
        mx, my = pygame.mouse.get_pos()
        for opt in self.options:
            rect = pygame.Rect(self.rect.centerx - 100, y, 200, 40)
            is_hovered = rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, rect, opt, self.font, is_hovered)
            self.button_rects.append((rect, opt.lower().replace(" ", "_")))
            y += 60

    def handle_click(self, pos) -> Optional[str]:
        for rect, action in self.button_rects:
            if rect.collidepoint(pos):
                return action
        return None
