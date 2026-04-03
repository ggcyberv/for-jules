import pygame
from typing import List, Optional
from party.character import Character
from ui.ui_helper import UIHelper, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_HP_RED, COLOR_FRAME_GOLD

class CombatView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.font = pygame.font.SysFont("Arial", 14)
        self.medium_font = pygame.font.SysFont("Arial", 16)
        self.large_font = pygame.font.SysFont("Arial", 22)
        self.button_rects: List[pygame.Rect] = []
        self.sprites = self._load_sprites()
        self.effects = []

    def _load_sprites(self):
        sprites = {}
        import os
        path = "data/sprites"
        for f in os.listdir(path):
            if f.endswith(".png"):
                name = f.split(".")[0]
                sprites[name] = pygame.image.load(os.path.join(path, f)).convert_alpha()
        return sprites

    def render(self, screen: pygame.Surface, party: List[Character], enemies: List[Character], log: List[str], turn: int, summary: Optional[str] = None):
        screen.fill((15, 15, 20))

        # Central Battle Log Frame
        log_rect = pygame.Rect(200, 350, 400, 150)
        UIHelper.draw_frame(screen, log_rect, border_color=(100, 100, 100))

        # Draw Party
        px, py = 120, 100
        for char in party:
            sprite = self.sprites.get(char.name.lower(), self.sprites.get("knight"))
            draw_sprite = sprite.copy()
            if char.hp <= 0: draw_sprite.set_alpha(100)
            screen.blit(pygame.transform.scale(draw_sprite, (64, 64)), (px - 32, py - 32))

            # Name and HP bar
            h_surf = self.medium_font.render(char.name, True, COLOR_TEXT_WHITE)
            screen.blit(h_surf, (px - 50, py + 35))
            UIHelper.draw_progress_bar(screen, px - 50, py + 55, 100, 8, char.hp, char.max_hp, COLOR_HP_RED)
            py += 100

        # Draw Enemies
        ex, ey = 680, 100
        for char in enemies:
            sprite = self.sprites.get(char.name.lower(), self.sprites.get("orc"))
            draw_sprite = sprite.copy()
            if char.hp <= 0: draw_sprite.set_alpha(100)
            screen.blit(pygame.transform.scale(draw_sprite, (64, 64)), (ex - 32, ey - 32))

            # Name and HP bar
            e_surf = self.medium_font.render(char.name, True, COLOR_TEXT_WHITE)
            screen.blit(e_surf, (ex - 50, ey + 35))
            # Assume max_hp for enemies if not present (simple placeholder)
            max_hp = getattr(char, 'max_hp', 50)
            UIHelper.draw_progress_bar(screen, ex - 50, ey + 55, 100, 8, char.hp, max_hp, COLOR_HP_RED)
            ey += 100

        # Draw Effects
        new_effects = []
        for fx_type, fx_pos, fx_timer in self.effects:
            sprite = self.sprites.get(fx_type, self.sprites.get("spark"))
            screen.blit(pygame.transform.scale(sprite, (64, 64)), (fx_pos[0] - 32, fx_pos[1] - 32))
            if fx_timer > 1: new_effects.append((fx_type, fx_pos, fx_timer - 1))
        self.effects = new_effects

        # Draw Log Entries
        ly = log_rect.y + 10
        for entry in log[-6:]:
            color = COLOR_TEXT_WHITE
            if "SEVERE" in entry: color = (255, 100, 100)
            elif "Victory" in entry: color = (100, 255, 100)
            elif "POWER STRIKE" in entry: color = COLOR_TEXT_GOLD
            lsurf = self.font.render(entry, True, color)
            screen.blit(lsurf, (log_rect.x + 10, ly))
            ly += 20

        if summary:
            s_surf = self.large_font.render(summary, True, COLOR_TEXT_GOLD)
            screen.blit(s_surf, (self.width // 2 - s_surf.get_width() // 2, 250))

        # Interventions
        self.button_rects = []
        btn_y = 510
        actions = ["heal", "strike", "taunt", "focus", "retreat"]

        # Add hero skills as actions
        for hero in party:
            if hero.hp > 0:
                for skill in hero.skills:
                    if skill.name.lower() not in actions:
                        actions.insert(0, skill.name.lower())

        mx, my = pygame.mouse.get_pos()
        for action in actions:
            rect = pygame.Rect(self.width // 2 - 100, btn_y, 200, 25)
            is_hovered = rect.collidepoint(mx, my)
            UIHelper.draw_button(screen, rect, f"Intervene: {action.capitalize()}", self.font, is_hovered)
            self.button_rects.append(rect)
            btn_y += 30

        # Title and Instructions
        title_text = f"BATTLE ROUND {turn}"
        t_surf = self.large_font.render(title_text, True, COLOR_TEXT_GOLD)
        screen.blit(t_surf, (self.width // 2 - t_surf.get_width() // 2, 20))

        text = "SPACE: Next Round | ESC: Finalize"
        surf = self.font.render(text, True, (200, 200, 200))
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, self.height - 30))

    def handle_click(self, pos, party: List[Character]) -> Optional[str]:
        actions = ["heal", "strike", "taunt", "focus", "retreat"]
        for hero in party:
            if hero.hp > 0:
                for skill in hero.skills:
                    if skill.name.lower() not in actions:
                        actions.insert(0, skill.name.lower())

        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                return actions[i]
        return None
