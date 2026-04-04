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
        self.options = ["New Game", "Load Game", "Settings", "Quit"]
        self.seed_input = ""
        self.input_rect = pygame.Rect(screen_width // 2 - 100, 250, 200, 32)
        self.random_rect = pygame.Rect(screen_width // 2 + 110, 250, 80, 32)
        self.active = False

    def render(self, screen: pygame.Surface):
        mx, my = pygame.mouse.get_pos()
        screen.fill((10, 10, 15))

        # Title
        title_surf = self.title_font.render("Chronicles of the Unbound Realm", True, COLOR_TEXT_GOLD)
        title_rect = title_surf.get_rect(center=(self.width // 2, 150))
        screen.blit(title_surf, title_rect)

        # Seed Input
        UIHelper.draw_frame(screen, self.input_rect, border_color=(COLOR_TEXT_GOLD if self.active else (100, 100, 100)))
        seed_label = self.font.render("World Seed:", True, COLOR_TEXT_WHITE)
        screen.blit(seed_label, (self.input_rect.x - 120, self.input_rect.y + 5))

        txt_surf = self.font.render(self.seed_input, True, COLOR_TEXT_WHITE)
        screen.blit(txt_surf, (self.input_rect.x + 5, self.input_rect.y + 5))

        # Randomize Button
        UIHelper.draw_button(screen, self.random_rect, "RAND", pygame.font.SysFont("Arial", 14), self.random_rect.collidepoint(mx, my))

        # Buttons
        self.button_rects = []
        start_y = 320

        for option in self.options:
            rect = pygame.Rect(self.width // 2 - 100, start_y, 200, 50)
            is_hovered = rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, rect, option, self.font, is_hovered)
            self.button_rects.append(rect)
            start_y += 70

    def handle_click(self, pos) -> Optional[str]:
        if self.input_rect.collidepoint(pos):
            self.active = True
        elif self.random_rect.collidepoint(pos):
            import secrets
            self.seed_input = secrets.token_hex(4)
            self.active = False
        else:
            self.active = False

        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                return self.options[i].lower().replace(" ", "_")
        return None

    def handle_keydown(self, event: pygame.event.Event):
        if self.active:
            if event.key == pygame.K_BACKSPACE:
                self.seed_input = self.seed_input[:-1]
            else:
                if len(self.seed_input) < 16 and event.unicode.isalnum():
                    self.seed_input += event.unicode
