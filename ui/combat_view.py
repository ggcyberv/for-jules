import pygame
from typing import List, Optional
from party.character import Character

class CombatView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.SysFont("Arial", 14)
        self.large_font = pygame.font.SysFont("Arial", 20)
        self.button_rects: List[pygame.Rect] = []

    def render(self, screen: pygame.Surface, party: List[Character], enemies: List[Character], log: List[str], turn: int, summary: Optional[str] = None):
        screen.fill((20, 10, 10))

        # Draw Party
        px, py = 100, 100
        for char in party:
            color = (0, 255, 0) if char.hp > 0 else (100, 0, 0)
            pygame.draw.circle(screen, color, (px, py), 20)
            hp_text = f"{char.name}: {char.hp}/{char.max_hp}"
            surf = self.font.render(hp_text, True, (255, 255, 255))
            screen.blit(surf, (px - 40, py + 25))
            py += 80

        # Draw Enemies
        ex, ey = 700, 100
        for char in enemies:
            color = (255, 0, 0) if char.hp > 0 else (100, 0, 0)
            pygame.draw.circle(screen, color, (ex, ey), 20)
            hp_text = f"{char.name}: {char.hp}"
            surf = self.font.render(hp_text, True, (255, 255, 255))
            screen.blit(surf, (ex - 40, ey + 25))
            ey += 80

        # Draw Log
        ly = 300
        for entry in log[-10:]:
            color = (255, 255, 255)
            if "SEVERE" in entry: color = (255, 100, 100)
            elif "Victory" in entry: color = (100, 255, 100)
            lsurf = self.font.render(entry, True, color)
            screen.blit(lsurf, (250, ly))
            ly += 20

        if summary:
            s_surf = self.large_font.render(summary, True, (255, 215, 0))
            screen.blit(s_surf, (self.width // 2 - s_surf.get_width() // 2, 250))

        # Interventions
        self.button_rects = []
        btn_y = 500
        actions = ["heal", "strike", "retreat"]
        for action in actions:
            rect = pygame.Rect(300, btn_y, 200, 25)
            pygame.draw.rect(screen, (80, 80, 80), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            atext = self.font.render(f"Intervene: {action.capitalize()}", True, (255, 255, 255))
            screen.blit(atext, (rect.x + 10, rect.y + 3))
            self.button_rects.append(rect)
            btn_y += 30

        # Instructions
        text = "SPACE: Next Round | ESC: Finalize"
        surf = self.font.render(text, True, (200, 200, 200))
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, self.height - 30))

    def handle_click(self, pos) -> Optional[str]:
        actions = ["heal", "strike", "retreat"]
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                return actions[i]
        return None
