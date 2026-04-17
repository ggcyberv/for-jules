import pygame
from typing import Tuple, Dict
from world.dungeon_generator import DungeonMap, DungeonTile
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_FRAME_GOLD
from typing import List

class DungeonView:
    def __init__(self, screen_width: int, screen_height: int, tile_size: int = 20):
        self.width = screen_width
        self.height = screen_height
        self.tile_size = tile_size
        self.font = pygame.font.SysFont("Arial", 12)
        self.medium_font = pygame.font.SysFont("Arial", 14)
        self.hover_timer = 0
        self.last_hover_tile = None

    def render(self, screen: pygame.Surface, dungeon: DungeonMap, party_pos: Tuple[int, int]):
        dt = 1/30
        screen.fill((0, 0, 0))

        # Center view on party
        offset_x = self.width // 2 - party_pos[0] * self.tile_size
        offset_y = self.height // 2 - party_pos[1] * self.tile_size

        for (x, y), tile in dungeon.tiles.items():
            if not tile.explored: continue

            color = (50, 50, 50) # Explored but not visible
            if tile.visible:
                color = (200, 200, 200) if not tile.is_wall else (100, 100, 100)

            rect = (offset_x + x * self.tile_size, offset_y + y * self.tile_size, self.tile_size, self.tile_size)
            pygame.draw.rect(screen, color, rect)

            # Floor Pattern
            if not tile.is_wall and tile.visible:
                if (x + y) % 2 == 0:
                    pygame.draw.rect(screen, (190, 190, 190), rect, 1)

            pygame.draw.rect(screen, (30, 30, 30), rect, 1) # Border

            if (x, y) == dungeon.exit_pos and tile.visible:
                pygame.draw.circle(screen, (0, 255, 0), (int(offset_x + x * self.tile_size + self.tile_size/2),
                                                        int(offset_y + y * self.tile_size + self.tile_size/2)), self.tile_size/3)

            if hasattr(tile, 'has_loot') and tile.has_loot and tile.visible:
                # Draw Chest
                pygame.draw.rect(screen, (255, 215, 0), (offset_x + x * self.tile_size + 4, offset_y + y * self.tile_size + 4, self.tile_size - 8, self.tile_size - 8))

            if hasattr(tile, 'enemies') and tile.enemies and tile.visible:
                # Draw Enemy placeholder (red circle)
                pygame.draw.circle(screen, (255, 0, 0), (int(offset_x + x * self.tile_size + self.tile_size/2),
                                                       int(offset_y + y * self.tile_size + self.tile_size/2)), self.tile_size/3)

        # Draw Party
        px, py = party_pos
        pygame.draw.circle(screen, (255, 215, 0), (int(offset_x + px * self.tile_size + self.tile_size/2),
                                                int(offset_y + py * self.tile_size + self.tile_size/2)), self.tile_size/2)

        # Instructions
        footer_rect = pygame.Rect(0, self.height - 40, self.width, 40)
        UIHelper.draw_frame(screen, footer_rect, border_width=1)
        text = "Use Arrow Keys to move in dungeon. Escape to Exit."
        surf = self.font.render(text, True, (255, 255, 255))
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, self.height - 30))

        # Tooltips
        mx, my = pygame.mouse.get_pos()
        # Convert mouse to dungeon coords
        tx = (mx - offset_x) // self.tile_size
        ty = (my - offset_y) // self.tile_size

        if (tx, ty) == self.last_hover_tile:
            self.hover_timer += dt
        else:
            self.hover_timer = 0
            self.last_hover_tile = (tx, ty)

        tile = dungeon.get_tile(tx, ty)
        if tile and tile.visible and self.hover_timer >= 0.5:
            lines = ["Wall" if tile.is_wall else "Floor"]
            if hasattr(tile, 'trap_id') and tile.trap_id:
                # Only show if party has high perception? For now always if visible.
                lines.append(f"TRAP: {tile.trap_id}")
            if hasattr(tile, 'has_loot') and tile.has_loot:
                lines.append("LOOT: Treasure Chest")
            if hasattr(tile, 'enemies') and tile.enemies:
                lines.append(f"ENEMY: {tile.enemies[0].capitalize()}")
            if (tx, ty) == dungeon.exit_pos:
                lines.append("EXIT: Stairs Up")

            self._render_tooltip(screen, mx, my, lines)

    def _render_tooltip(self, screen, x, y, lines: List[str]):
        padding = 8
        line_surfs = [self.medium_font.render(l, True, COLOR_TEXT_WHITE) for l in lines]
        width = max(s.get_width() for s in line_surfs) if line_surfs else 0
        height = sum(s.get_height() + 3 for s in line_surfs)

        rect = pygame.Rect(x + 10, y + 10, width + padding * 2, height + padding * 2)
        if rect.right > self.width: rect.right = x - 10
        if rect.bottom > self.height: rect.bottom = y - 10

        UIHelper.draw_frame(screen, rect, border_color=COLOR_FRAME_GOLD, bg_color=(20, 20, 25), border_width=1)
        curr_y = rect.y + padding
        for surf in line_surfs:
            screen.blit(surf, (rect.x + padding, curr_y))
            curr_y += surf.get_height() + 3
