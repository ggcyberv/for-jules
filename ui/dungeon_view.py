import pygame
from typing import Tuple, Dict
from world.dungeon_generator import DungeonMap, DungeonTile

class DungeonView:
    def __init__(self, screen_width: int, screen_height: int, tile_size: int = 20):
        self.width = screen_width
        self.height = screen_height
        self.tile_size = tile_size
        self.font = pygame.font.SysFont("Arial", 12)

    def render(self, screen: pygame.Surface, dungeon: DungeonMap, party_pos: Tuple[int, int]):
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

        # Draw Party
        px, py = party_pos
        pygame.draw.circle(screen, (255, 215, 0), (int(offset_x + px * self.tile_size + self.tile_size/2),
                                                int(offset_y + py * self.tile_size + self.tile_size/2)), self.tile_size/2)

        # Instructions
        text = "Use Arrow Keys to move in dungeon. Escape to Exit."
        surf = self.font.render(text, True, (255, 255, 255))
        screen.blit(surf, (10, self.height - 30))
