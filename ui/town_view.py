import pygame
from typing import List, Optional
from world.location import Town, TownNode

class TownView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.SysFont("Arial", 18)
        self.large_font = pygame.font.SysFont("Arial", 24)
        self.node_rects: List[pygame.Rect] = []

    def render(self, screen: pygame.Surface, town: Town):
        screen.fill((50, 40, 30)) # Brownish town background

        # Town Name
        title_surf = self.large_font.render(f"Town: {town.name}", True, (255, 215, 0))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 50))

        # Nodes
        self.node_rects = []
        y = 150
        for i, node in enumerate(town.nodes):
            rect = pygame.Rect(self.width // 2 - 200, y, 400, 40)
            pygame.draw.rect(screen, (80, 70, 60), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

            node_text = f"{i+1}. {node.name} - {node.description}"
            surf = self.font.render(node_text, True, (255, 255, 255))
            screen.blit(surf, (rect.x + 10, rect.y + 10))

            self.node_rects.append(rect)
            y += 50

        # Footer
        footer_text = "Click to select a service node. Press ESC to leave town."
        footer_surf = self.font.render(footer_text, True, (200, 200, 200))
        screen.blit(footer_surf, (self.width // 2 - footer_surf.get_width() // 2, self.height - 50))

    def handle_click(self, pos) -> Optional[int]:
        for i, rect in enumerate(self.node_rects):
            if rect.collidepoint(pos):
                return i
        return None
