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
    "dungeon": (80, 0, 0),
    "grid": (50, 50, 50),
    "unknown": (20, 20, 20),
    "sidebar": (40, 40, 40),
    "text": (220, 220, 220)
}

class Renderer:
    def __init__(self, screen_width: int, screen_height: int, hex_size: int):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sidebar_width = 200
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("D&D World Simulator")
        self.hex_size = hex_size # radius
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 18, bold=True)

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

    def draw_sidebar(self, state: Dict[str, Any]):
        rect = (self.screen_width - self.sidebar_width, 0, self.sidebar_width, self.screen_height)
        pygame.draw.rect(self.screen, COLORS["sidebar"], rect)

        y_offset = 20
        # Assume first hero is the player's party
        if state.get("party_info"):
            for char in state["party_info"]:
                title = self.title_font.render(f"{char['name']}", True, COLORS["text"])
                self.screen.blit(title, (self.screen_width - self.sidebar_width + 10, y_offset))
                y_offset += 25

                info = self.font.render(f"{char['class']} Lvl {char['level']}", True, COLORS["text"])
                self.screen.blit(info, (self.screen_width - self.sidebar_width + 10, y_offset))
                y_offset += 20

                hp = self.font.render(f"HP: {char['hp']}/{char['max_hp']}", True, COLORS["text"])
                self.screen.blit(hp, (self.screen_width - self.sidebar_width + 10, y_offset))
                y_offset += 30

        # Draw log snippet
        if state.get("log"):
            log_title = self.title_font.render("Log", True, COLORS["text"])
            self.screen.blit(log_title, (self.screen_width - self.sidebar_width + 10, y_offset))
            y_offset += 25
            for entry in state["log"][-10:]:
                # Truncate entry if too long
                txt = entry[:25] + "..." if len(entry) > 25 else entry
                log_entry = self.font.render(txt, True, COLORS["text"])
                self.screen.blit(log_entry, (self.screen_width - self.sidebar_width + 10, y_offset))
                y_offset += 18

    def render_map(self, state: Dict[str, Any]):
        self.screen.fill((0, 0, 0))

        # Draw tiles
        for tile in state["tiles"]:
            if tile.get("discovered", True):
                self.draw_hex(tile["x"], tile["y"], tile["terrain"])
                if tile["poi"]:
                    self.draw_poi(tile["x"], tile["y"], tile["poi"]["type"], tile["poi"]["owner"])
            else:
                self.draw_hex(tile["x"], tile["y"], "unknown")

        # Draw heroes
        for hero in state["heroes"]:
            # Only draw hero if on discovered tile (simplified)
            self.draw_hero(hero["x"], hero["y"], hero["owner"])

        self.draw_sidebar(state)

        pygame.display.flip()
