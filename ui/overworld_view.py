import pygame
import math
from typing import Tuple, List, Optional, Dict
from world.hex_grid import HexGrid, HexTile
from engine.game_state import GameState
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_FRAME_GOLD, COLOR_HP_RED, COLOR_AP_BLUE, COLOR_XP_GREEN

class OverworldView:
    def __init__(self, screen_width: int, screen_height: int, hex_size: int = 30):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hex_size = hex_size
        self.font = pygame.font.SysFont("Arial", 12)
        self.medium_font = pygame.font.SysFont("Arial", 14)
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
        screen.fill((20, 20, 25)) # Darker BG

        # Draw Hex Grid
        for (q, r), tile in grid.tiles.items():
            px, py = self.hex_to_pixel(q, r)
            if px < -50 or px > self.screen_width - 200 or py < -50 or py > self.screen_height + 50:
                continue

            color = (40, 40, 45) if not tile.discovered else (50, 120, 50)
            if tile.terrain_type == "mountain": color = (80, 80, 80)
            elif tile.terrain_type == "forest": color = (30, 90, 30)
            elif tile.terrain_type == "water": color = (30, 30, 150)

            points = []
            for i in range(6):
                angle_rad = math.pi / 180 * (60 * i)
                points.append((px + self.hex_size * math.cos(angle_rad),
                             py + self.hex_size * math.sin(angle_rad)))

            pygame.draw.polygon(screen, color, points)
            border_color = (60, 60, 70)
            if tile.faction_influence == "citizens": border_color = (80, 80, 180)
            elif tile.faction_influence == "bandits": border_color = (180, 80, 80)
            pygame.draw.polygon(screen, border_color, points, 1)

            if tile.poi_id:
                poi_color = COLOR_TEXT_GOLD
                if "dungeon" in tile.poi_id or "loc" in tile.poi_id: poi_color = (200, 50, 50)
                pygame.draw.rect(screen, poi_color, (px - 5, py - 5, 10, 10))

            if (q, r) == party_pos:
                pygame.draw.circle(screen, COLOR_TEXT_GOLD, (int(px), int(py)), self.hex_size // 2)

        state = GameState()

        # Right Side Panel
        panel_rect = pygame.Rect(self.screen_width - 250, 0, 250, self.screen_height)
        UIHelper.draw_frame(screen, panel_rect)

        # Party Status in Panel
        y = 20
        title_surf = self.large_font.render("The Party", True, COLOR_TEXT_GOLD)
        screen.blit(title_surf, (panel_rect.x + 20, y))
        y += 40

        for hero in state.party.members:
            h_name = self.medium_font.render(hero.name, True, COLOR_TEXT_WHITE)
            screen.blit(h_name, (panel_rect.x + 20, y))
            UIHelper.draw_progress_bar(screen, panel_rect.x + 20, y + 20, 200, 10, hero.hp, hero.max_hp, COLOR_HP_RED)
            UIHelper.draw_progress_bar(screen, panel_rect.x + 20, y + 32, 200, 5, hero.xp % 100, 100, COLOR_XP_GREEN)
            y += 50

        # Resources
        y += 20
        res_text = f"Gold: {state.party.gold} | Food: {state.party.food}"
        res_surf = self.medium_font.render(res_text, True, COLOR_TEXT_GOLD)
        screen.blit(res_surf, (panel_rect.x + 20, y))
        y += 30

        ap_text = f"AP: {state.party.current_ap}"
        screen.blit(self.medium_font.render(ap_text, True, COLOR_AP_BLUE), (panel_rect.x + 20, y))
        y += 30

        # Turn count
        turn_text = f"Turn: {state.turn}"
        screen.blit(self.medium_font.render(turn_text, True, COLOR_TEXT_WHITE), (panel_rect.x + 20, y))
        y += 40

        # Logs in Panel
        log_title = self.medium_font.render("Chronicle:", True, COLOR_TEXT_GOLD)
        screen.blit(log_title, (panel_rect.x + 20, y))
        y += 25
        for log in logs[-8:]:
            y += UIHelper.render_text_wrapped(screen, f"> {log}", (panel_rect.x + 20, y), self.font, 210, (200, 200, 200))
            y += 5

        # Top Bar hint
        hint_text = "SPACE: End Turn | S: Save | L: Load | I: Party"
        hint_surf = self.font.render(hint_text, True, (150, 150, 150))
        screen.blit(hint_surf, (10, 10))

        # Minimap
        self._render_minimap(screen, grid, party_pos)

        # Improved Tooltip handling
        mx, my = pygame.mouse.get_pos()
        tq, tr = self.pixel_to_hex(mx, my)
        tile = grid.get_tile(tq, tr)
        if tile and tile.poi_id and tile.discovered:
            loc = state.locations.get(tile.poi_id)
            if loc:
                self._render_tooltip(screen, mx, my, f"{loc.name} ({loc.location_type})")

    def _render_minimap(self, screen, grid, party_pos):
        mini_size = 120
        mini_rect = pygame.Rect(10, self.screen_height - mini_size - 10, mini_size, mini_size)
        UIHelper.draw_frame(screen, mini_rect, border_color=(100, 100, 100), bg_color=(10, 10, 10), border_width=1)

        # Center of minimap corresponds to party_pos
        scale = mini_size / 20 # Show 20 hexes across
        for (q, r), tile in grid.tiles.items():
            if not tile.discovered: continue

            dq, dr = q - party_pos[0], r - party_pos[1]
            if abs(dq) > 10 or abs(dr) > 10: continue

            mx = mini_rect.centerx + dq * scale
            my = mini_rect.centery + dr * scale

            color = (50, 120, 50)
            if tile.terrain_type == "mountain": color = (100, 100, 100)
            elif tile.terrain_type == "water": color = (50, 50, 200)
            elif tile.poi_id: color = COLOR_TEXT_GOLD

            pygame.draw.rect(screen, color, (mx - scale/2, my - scale/2, scale - 1, scale - 1))

        # Party dot
        pygame.draw.circle(screen, (255, 255, 255), mini_rect.center, 3)

    def _render_tooltip(self, screen, x, y, text):
        surf = self.medium_font.render(text, True, COLOR_TEXT_WHITE)
        padding = 8
        rect = pygame.Rect(x + 10, y + 10, surf.get_width() + padding * 2, surf.get_height() + padding * 2)
        # Keep tooltip on screen
        if rect.right > self.screen_width: rect.right = x - 10
        if rect.bottom > self.screen_height: rect.bottom = y - 10

        UIHelper.draw_frame(screen, rect, border_color=(150, 150, 150), bg_color=(20, 20, 20), border_width=1)
        screen.blit(surf, (rect.x + padding, rect.y + padding))
