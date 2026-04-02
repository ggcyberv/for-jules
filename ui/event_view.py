import pygame
from typing import List, Optional
from events.event_template import EventTemplate, EventChoice

class EventView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 600
        self.height = 400
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.choice_rects: List[pygame.Rect] = []

    def render(self, screen: pygame.Surface, event: EventTemplate):
        # Draw background
        pygame.draw.rect(screen, (20, 20, 20), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        # Title
        title_surf = self.font.render(event.title, True, (255, 215, 0))
        screen.blit(title_surf, (self.rect.x + 20, self.rect.y + 20))

        # Description
        words = event.description.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.small_font.size(test_line)[0] < self.width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        y = self.rect.y + 60
        for line in lines:
            line_surf = self.small_font.render(line, True, (220, 220, 220))
            screen.blit(line_surf, (self.rect.x + 20, y))
            y += 20

        # Choices
        self.choice_rects = []
        y = self.rect.y + 250
        for i, choice in enumerate(event.choices):
            choice_rect = pygame.Rect(self.rect.x + 20, y, self.width - 40, 30)
            pygame.draw.rect(screen, (50, 50, 50), choice_rect)
            pygame.draw.rect(screen, (150, 150, 150), choice_rect, 1)

            choice_text = f"{i+1}. {choice.text}"
            choice_surf = self.small_font.render(choice_text, True, (255, 255, 255))
            screen.blit(choice_surf, (choice_rect.x + 10, choice_rect.y + 5))

            self.choice_rects.append(choice_rect)
            y += 40

    def handle_click(self, pos) -> Optional[int]:
        for i, rect in enumerate(self.choice_rects):
            if rect.collidepoint(pos):
                return i
        return None
