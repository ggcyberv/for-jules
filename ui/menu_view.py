import pygame
from typing import Optional, List
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE

class MenuView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.button_rects: List[pygame.Rect] = []
        self.options = ["New Game", "Load Game", "Quit"]

    def render(self, screen: pygame.Surface):
        screen.fill((10, 10, 15))

        # Title
        title_surf = self.title_font.render("Chronicles of the Unbound Realm", True, COLOR_TEXT_GOLD)
        title_rect = title_surf.get_rect(center=(self.width // 2, 150))
        screen.blit(title_surf, title_rect)

        # Buttons
        self.button_rects = []
        start_y = 300
        mx, my = pygame.mouse.get_pos()

        for option in self.options:
            rect = pygame.Rect(self.width // 2 - 100, start_y, 200, 50)
            is_hovered = rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, rect, option, self.font, is_hovered)
            self.button_rects.append(rect)
            start_y += 70

    def handle_click(self, pos) -> Optional[str]:
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                return self.options[i].lower().replace(" ", "_")
        return None
