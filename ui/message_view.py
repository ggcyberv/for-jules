import pygame
from typing import Optional
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE

class MessageView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 400
        self.height = 200
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 16)
        self.title_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.active_message: Optional[dict] = None
        self.button_rect = pygame.Rect(self.rect.centerx - 50, self.rect.bottom - 40, 100, 30)

    def show(self, title: str, text: str):
        self.active_message = {"title": title, "text": text}

    def render(self, screen: pygame.Surface):
        if not self.active_message:
            return

        UIHelper.draw_frame(screen, self.rect, border_color=(200, 200, 200))

        # Title
        t_surf = self.title_font.render(self.active_message["title"], True, COLOR_TEXT_GOLD)
        screen.blit(t_surf, (self.rect.x + 20, self.rect.y + 20))

        # Text
        UIHelper.render_text_wrapped(screen, self.active_message["text"], (self.rect.x + 20, self.rect.y + 60), self.font, self.width - 40)

        # OK Button
        mx, my = pygame.mouse.get_pos()
        UIHelper.draw_button(screen, self.button_rect, "OK", self.font, self.button_rect.collidepoint(mx, my))

    def handle_click(self, pos) -> bool:
        if self.active_message and self.button_rect.collidepoint(pos):
            self.active_message = None
            return True
        return False
