import pygame
import math
from typing import Tuple, List, Optional, Dict
from world.hex_grid import HexGrid, HexTile
from engine.game_state import GameState

class OverworldView:
    def __init__(self, screen_width: int, screen_height: int, hex_size: int = 30):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hex_size = hex_size
        self.font = pygame.font.SysFont("Arial", 12)
        self.large_font = pygame.font.SysFont("Arial", 18)
        self.camera_offset = [0, 0]

    def hex_to_pixel(self, q: int, r: int) -> Tuple[float, float]:
        x = self.hex_size * (3/2 * q)
        y = self.hex_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return x + self.camera_offset[0], y + self.camera_offset[1]

    def pixel_to_hex(self, px: float, py: float) -> Tuple[int, int]:
        px -= self.camera_offset[0]
        py -= self.camera_offset[1]
        q = (2/3 * px) / self.hex_size
        r = (-1/3 * px + math.sqrt(3)/3 * py) / self.hex_size
        x, y, z = q, r, -q - r
        rx, ry, rz = round(x), round(y), round(z)
        dx, dy, dz = abs(rx - x), abs(ry - y), abs(rz - z)
        if dx > dy and dx > dz: rx = -ry - rz
        elif dy > dz: ry = -rx - rz
        else: rz = -rx - ry
        return int(rx), int(ry)

    def update_camera(self, party_pos: Tuple[int, int]):
        tx = self.hex_size * (3/2 * party_pos[0])
        ty = self.hex_size * (math.sqrt(3)/2 * party_pos[0] + math.sqrt(3) * party_pos[1])
        self.camera_offset[0] = self.screen_width // 2 - tx
        self.camera_offset[1] = self.screen_height // 2 - ty

    def render(self, screen: pygame.Surface, grid: HexGrid, party_pos: Tuple[int, int], logs: List[str]):
        self.update_camera(party_pos)
        screen.fill((30, 30, 30))

        for (q, r), tile in grid.tiles.items():
            px, py = self.hex_to_pixel(q, r)
            if px < -50 or px > self.screen_width + 50 or py < -50 or py > self.screen_height + 50:
                continue

            color = (60, 60, 60) if not tile.discovered else (50, 150, 50)
            if tile.terrain_type == "mountain": color = (100, 100, 100)
            elif tile.terrain_type == "forest": color = (34, 139, 34)
            elif tile.terrain_type == "water": color = (0, 0, 255)

            points = []
            for i in range(6):
                angle_rad = math.pi / 180 * (60 * i)
                points.append((px + self.hex_size * math.cos(angle_rad),
                             py + self.hex_size * math.sin(angle_rad)))

            pygame.draw.polygon(screen, color, points)
            border_color = (150, 150, 150)
            if tile.faction_influence == "citizens": border_color = (100, 100, 255)
            elif tile.faction_influence == "bandits": border_color = (255, 100, 100)
            pygame.draw.polygon(screen, border_color, points, 2)

            if tile.poi_id:
                poi_color = (255, 255, 0)
                if "dungeon" in tile.poi_id or "loc" in tile.poi_id: poi_color = (200, 50, 50)
                pygame.draw.rect(screen, poi_color, (px - 5, py - 5, 10, 10))

            if (q, r) == party_pos:
                pygame.draw.circle(screen, (255, 215, 0), (int(px), int(py)), self.hex_size // 2)

        state = GameState()
        ui_text = f"Turn: {state.turn} | Gold: {state.party.gold} | Food: {state.party.food} | AP: {state.party.current_ap}"
        text_surf = self.font.render(ui_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        rep_y = 50
        for faction_id, rep in state.faction_system.reputations.items():
            status = state.faction_system.get_status(faction_id)
            rep_text = f"Faction {faction_id}: {rep} ({status})"
            rep_surf = self.font.render(rep_text, True, (255, 255, 100))
            screen.blit(rep_surf, (self.screen_width - 200, rep_y))
            rep_y += 15

        y = 30
        for hero in state.party.members:
            hero_text = f"{hero.name}: HP {hero.hp}/{hero.max_hp} | LVL {hero.level}"
            hero_surf = self.font.render(hero_text, True, (200, 255, 200))
            screen.blit(hero_surf, (10, y))
            y += 15

        log_y = 500
        for log in logs[-5:]:
            log_surf = self.font.render(log, True, (200, 200, 200))
            screen.blit(log_surf, (10, log_y))
            log_y += 15

        hint_text = "SPACE: End Turn | S: Save | L: Load | T: Tactics | I: Party"
        hint_surf = self.font.render(hint_text, True, (150, 150, 150))
        screen.blit(hint_surf, (500, 10))

        # Improved Tooltip handling
        mx, my = pygame.mouse.get_pos()
        tq, tr = self.pixel_to_hex(mx, my)
        tile = grid.get_tile(tq, tr)
        if tile and tile.poi_id and tile.discovered:
            loc = state.locations.get(tile.poi_id)
            if loc:
                self._render_tooltip(screen, mx, my, f"{loc.name} ({loc.location_type})")

    def _render_tooltip(self, screen, x, y, text):
        surf = self.font.render(text, True, (255, 255, 255))
        padding = 5
        rect = pygame.Rect(x + 10, y + 10, surf.get_width() + padding * 2, surf.get_height() + padding * 2)
        # Keep tooltip on screen
        if rect.right > self.screen_width: rect.right = x - 10
        if rect.bottom > self.screen_height: rect.bottom = y - 10
        pygame.draw.rect(screen, (0, 0, 0), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        screen.blit(surf, (rect.x + padding, rect.y + padding))
