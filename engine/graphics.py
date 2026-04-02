import pygame
import math
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
    def __init__(self, screen_width: int, screen_height: int, hex_size: int):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Heroes Strategy Prototype - Hex Map")
        self.hex_size = hex_size # radius
        self.font = pygame.font.SysFont("Arial", 14)

    def hex_to_pixel(self, x: int, y: int) -> Tuple[float, float]:
        """Convert pointy-top odd-r offset to pixel."""
        # Pointy top hexagon math:
        # width = sqrt(3) * size
        # spacing_x = width
        # spacing_y = 3/2 * size
        width = math.sqrt(3) * self.hex_size
        px = width * (x + 0.5 * (y & 1))
        py = self.hex_size * 3/2 * y
        return px + width, py + self.hex_size

    def draw_hex(self, x: int, y: int, terrain_type: str):
        center_x, center_y = self.hex_to_pixel(x, y)
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            px = center_x + self.hex_size * math.cos(angle_rad)
            py = center_y + self.hex_size * math.sin(angle_rad)
            points.append((px, py))

        color = COLORS.get(terrain_type, COLORS["plains"])
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, COLORS["grid"], points, 1)

    def draw_poi(self, x: int, y: int, poi_type: str, owner_id: int):
        center_x, center_y = self.hex_to_pixel(x, y)
        center = (int(center_x), int(center_y))
        radius = self.hex_size // 2
        color = COLORS.get(poi_type, (255, 255, 255))
        pygame.draw.circle(self.screen, color, center, radius)

        # Draw owner indicator
        owner_color = (255, 255, 255)
        if owner_id == 1: owner_color = COLORS["hero_p1"]
        elif owner_id == 2: owner_color = COLORS["hero_p2"]
        pygame.draw.circle(self.screen, owner_color, center, radius // 2)

    def draw_hero(self, x: int, y: int, owner_id: int):
        center_x, center_y = self.hex_to_pixel(x, y)
        rect_size = self.hex_size // 1.5
        rect = (center_x - rect_size // 2, center_y - rect_size // 2, rect_size, rect_size)
        color = COLORS["hero_p1"] if owner_id == 1 else COLORS["hero_p2"]
        pygame.draw.rect(self.screen, color, rect)

    def render_map(self, state: Dict[str, Any]):
        self.screen.fill((0, 0, 0))

        # Draw tiles
        for tile in state["tiles"]:
            self.draw_hex(tile["x"], tile["y"], tile["terrain"])
            if tile["poi"]:
                self.draw_poi(tile["x"], tile["y"], tile["poi"]["type"], tile["poi"]["owner"])

        # Draw heroes
        for hero in state["heroes"]:
            self.draw_hero(hero["x"], hero["y"], hero["owner"])

        pygame.display.flip()
