import pygame
from typing import List, Optional
from events.event_template import EventTemplate, EventChoice
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE

class EventView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 600
        self.height = 400
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.choice_rects: List[pygame.Rect] = []

    def render(self, screen: pygame.Surface, event: EventTemplate):
        # Draw frame
        UIHelper.draw_frame(screen, self.rect)

        # Title
        title_surf = self.font.render(event.title, True, COLOR_TEXT_GOLD)
        screen.blit(title_surf, (self.rect.x + 30, self.rect.y + 30))

        # Description
        y = self.rect.y + 70
        y_offset = UIHelper.render_text_wrapped(screen, event.description, (self.rect.x + 30, y), self.small_font, self.width - 60)

        # Choices
        self.choice_rects = []
        y = self.rect.y + 240
        mx, my = pygame.mouse.get_pos()
        for i, choice in enumerate(event.choices):
            choice_rect = pygame.Rect(self.rect.x + 30, y, self.width - 60, 35)
            is_hovered = choice_rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, choice_rect, choice.text, self.small_font, is_hovered)

            self.choice_rects.append(choice_rect)
            y += 45

    def handle_click(self, pos) -> Optional[int]:
        for i, rect in enumerate(self.choice_rects):
            if rect.collidepoint(pos):
                return i
        return None
