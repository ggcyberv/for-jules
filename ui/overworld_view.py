import pygame
import math
from typing import Tuple, List, Optional
from world.hex_grid import HexGrid, HexTile
from engine.game_state import GameState

class OverworldView:
    def __init__(self, screen_width: int, screen_height: int, hex_size: int = 30):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hex_size = hex_size
        self.font = pygame.font.SysFont("Arial", 12)
        self.large_font = pygame.font.SysFont("Arial", 18)

    def hex_to_pixel(self, q: int, r: int) -> Tuple[float, float]:
        x = self.hex_size * (3/2 * q)
        y = self.hex_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return x + 100, y + 100 # Offset for visibility

    def pixel_to_hex(self, px: float, py: float) -> Tuple[int, int]:
        px -= 100
        py -= 100
        q = (2/3 * px) / self.hex_size
        r = (-1/3 * px + math.sqrt(3)/3 * py) / self.hex_size

        # Round axial to nearest hex
        x, y, z = q, r, -q - r
        rx, ry, rz = round(x), round(y), round(z)
        dx, dy, dz = abs(rx - x), abs(ry - y), abs(rz - z)
        if dx > dy and dx > dz: rx = -ry - rz
        elif dy > dz: ry = -rx - rz
        else: rz = -rx - ry
        return rx, ry

    def render(self, screen: pygame.Surface, grid: HexGrid, party_pos: Tuple[int, int], logs: List[str]):
        screen.fill((30, 30, 30))

        for (q, r), tile in grid.tiles.items():
            px, py = self.hex_to_pixel(q, r)

            # Draw hex background
            color = (80, 80, 80) if not tile.discovered else (50, 150, 50)
            if tile.terrain_type == "mountain": color = (100, 100, 100)
            elif tile.terrain_type == "forest": color = (34, 139, 34)
            elif tile.terrain_type == "water": color = (0, 0, 255)

            points = []
            for i in range(6):
                angle_deg = 60 * i
                angle_rad = math.pi / 180 * angle_deg
                points.append((px + self.hex_size * math.cos(angle_rad),
                             py + self.hex_size * math.sin(angle_rad)))

            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (200, 200, 200), points, 1) # Border

            # Draw POI
            if tile.poi_id:
                poi_color = (255, 255, 0)
                if "dungeon" in tile.poi_id: poi_color = (200, 50, 50)
                pygame.draw.rect(screen, poi_color, (px - 5, py - 5, 10, 10))

            if (q, r) == party_pos:
                pygame.draw.circle(screen, (255, 215, 0), (int(px), int(py)), self.hex_size // 2)

        # UI Overlay
        state = GameState()
        ui_text = f"Turn: {state.turn} | Gold: {state.party.gold} | Food: {state.party.food} | AP: {state.party.current_ap}"
        text_surf = self.font.render(ui_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        # Faction Reputation
        rep_y = 50
        for faction_id, rep in state.faction_system.reputations.items():
            status = state.faction_system.get_status(faction_id)
            rep_text = f"Faction {faction_id}: {rep} ({status})"
            rep_surf = self.font.render(rep_text, True, (255, 255, 100))
            screen.blit(rep_surf, (self.screen_width - 200, rep_y))
            rep_y += 15

        # Hero Stats
        y = 30
        for hero in state.party.members:
            hero_text = f"{hero.name}: HP {hero.hp}/{hero.max_hp} | LVL {hero.level}"
            hero_surf = self.font.render(hero_text, True, (200, 255, 200))
            screen.blit(hero_surf, (10, y))
            y += 15

        # Log Overlay
        log_y = 500
        for log in logs[-5:]:
            log_surf = self.font.render(log, True, (200, 200, 200))
            screen.blit(log_surf, (10, log_y))
            log_y += 15

        # Controls Hint
        hint_text = "SPACE: End Turn | S: Save | L: Load | T: Tactics"
        hint_surf = self.font.render(hint_text, True, (150, 150, 150))
        screen.blit(hint_surf, (500, 10))
