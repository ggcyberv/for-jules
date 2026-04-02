import pygame
from typing import Tuple, Dict, List, Any

# Colors
COLORS = {
    "plains": (150, 200, 150),
    "forest": (34, 139, 34),
    "mountain": (139, 137, 137),
    "hero_p1": (0, 0, 255),
    "hero_p2": (255, 0, 0),
    "town": (200, 200, 0),
    "mine": (100, 100, 100),
    "fort": (150, 150, 255),
    "grid": (50, 50, 50)
}

class Renderer:
    def __init__(self, screen_width: int, screen_height: int, grid_size: int):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Heroes Strategy Prototype")
        self.grid_size = grid_size
        self.font = pygame.font.SysFont("Arial", 14)

    def draw_tile(self, x: int, y: int, terrain_type: str):
        rect = (x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
        color = COLORS.get(terrain_type, COLORS["plains"])
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, COLORS["grid"], rect, 1)

    def draw_poi(self, x: int, y: int, poi_type: str, owner_id: int):
        center = (x * self.grid_size + self.grid_size // 2, y * self.grid_size + self.grid_size // 2)
        radius = self.grid_size // 3
        color = COLORS.get(poi_type, (255, 255, 255))
        pygame.draw.circle(self.screen, color, center, radius)

        # Draw owner indicator
        owner_color = (255, 255, 255)
        if owner_id == 1: owner_color = COLORS["hero_p1"]
        elif owner_id == 2: owner_color = COLORS["hero_p2"]
        pygame.draw.circle(self.screen, owner_color, center, radius // 2)

    def draw_hero(self, x: int, y: int, owner_id: int):
        rect = (x * self.grid_size + self.grid_size // 4, y * self.grid_size + self.grid_size // 4,
                self.grid_size // 2, self.grid_size // 2)
        color = COLORS["hero_p1"] if owner_id == 1 else COLORS["hero_p2"]
        pygame.draw.rect(self.screen, color, rect)

    def render_map(self, state: Dict[str, Any]):
        self.screen.fill((0, 0, 0))

        # Draw tiles
        for tile in state["tiles"]:
            self.draw_tile(tile["x"], tile["y"], tile["terrain"])
            if tile["poi"]:
                self.draw_poi(tile["x"], tile["y"], tile["poi"]["type"], tile["poi"]["owner"])

        # Draw heroes
        for hero in state["heroes"]:
            self.draw_hero(hero["x"], hero["y"], hero["owner"])

        pygame.display.flip()
