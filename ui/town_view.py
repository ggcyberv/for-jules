import pygame
from typing import List, Optional
from world.location import Town, TownNode
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE

class TownView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.SysFont("Arial", 18)
        self.large_font = pygame.font.SysFont("Arial", 24)
        self.node_rects: List[pygame.Rect] = []

    def render(self, screen: pygame.Surface, town: Town):
        screen.fill((20, 20, 25))

        # Central Panel
        panel_rect = pygame.Rect(self.width // 2 - 250, 50, 500, 500)
        UIHelper.draw_frame(screen, panel_rect)

        # Town Name
        title_surf = self.large_font.render(f"{town.name}", True, COLOR_TEXT_GOLD)
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 80))

        # Nodes
        self.node_rects = []
        y = 160
        mx, my = pygame.mouse.get_pos()
        for i, node in enumerate(town.nodes):
            rect = pygame.Rect(self.width // 2 - 200, y, 400, 45)
            is_hovered = rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, rect, f"{node.name}", self.font, is_hovered)

            desc_surf = pygame.font.SysFont("Arial", 12).render(node.description, True, (200, 200, 200))
            screen.blit(desc_surf, (rect.x + 10, rect.bottom + 2))

            self.node_rects.append(rect)
            y += 70

        # Footer
        footer_text = "Click to select a service node. Press ESC to leave town."
        footer_surf = self.font.render(footer_text, True, (200, 200, 200))
        screen.blit(footer_surf, (self.width // 2 - footer_surf.get_width() // 2, self.height - 50))

    def handle_click(self, pos) -> Optional[int]:
        for i, rect in enumerate(self.node_rects):
            if rect.collidepoint(pos):
                return i
        return None
