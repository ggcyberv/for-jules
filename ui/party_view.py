import pygame
from typing import List, Optional
from party.party_manager import Party
from party.character import Character
from party.item import Item

class PartyView:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = 700
        self.height = 500
        self.rect = pygame.Rect((screen_width - self.width) // 2, (screen_height - self.height) // 2, self.width, self.height)
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 12)
        self.large_font = pygame.font.SysFont("Arial", 22)
        self.char_idx = 0
        self.attr_rects = []

    def render(self, screen: pygame.Surface, party: Party):
        pygame.draw.rect(screen, (30, 40, 50), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        for i, char in enumerate(party.members):
            tab_rect = pygame.Rect(self.rect.x + 20 + i * 110, self.rect.y + 20, 100, 30)
            color = (100, 120, 140) if i == self.char_idx else (60, 70, 80)
            pygame.draw.rect(screen, color, tab_rect)
            pygame.draw.rect(screen, (255, 255, 255), tab_rect, 1)
            name_surf = self.small_font.render(char.name, True, (255, 255, 255))
            screen.blit(name_surf, (tab_rect.x + 5, tab_rect.y + 7))

        if not party.members: return
        char = party.members[self.char_idx]

        detail_y = self.rect.y + 70
        title_surf = self.large_font.render(f"{char.name} (Level {char.level})", True, (255, 215, 0))
        screen.blit(title_surf, (self.rect.x + 20, detail_y))

        stats = [
            ("Attack", char.attack, char.effective_attack),
            ("Defense", char.defense, char.effective_defense),
            ("Speed", char.speed, char.effective_speed)
        ]

        self.attr_rects = []
        for i, (name, base, eff) in enumerate(stats):
            text = f"{name}: {eff} (Base: {base})"
            surf = self.font.render(text, True, (255, 255, 255))
            screen.blit(surf, (self.rect.x + 20, detail_y + 40 + i * 30))

            if char.attribute_points > 0:
                plus_rect = pygame.Rect(self.rect.x + 250, detail_y + 40 + i * 30, 20, 20)
                pygame.draw.rect(screen, (0, 150, 0), plus_rect)
                plus_surf = self.font.render("+", True, (255, 255, 255))
                screen.blit(plus_surf, (plus_rect.x + 5, plus_rect.y))
                self.attr_rects.append((plus_rect, name.lower()))

        # Level up info
        if char.attribute_points > 0:
            msg = f"Available Attribute Points: {char.attribute_points}"
            msg_surf = self.font.render(msg, True, (0, 255, 0))
            screen.blit(msg_surf, (self.rect.x + 20, detail_y + 140))

        # Equipment and Inventory as before...
        eq_y = detail_y + 40
        eq_x = self.rect.x + 350
        eq_title = self.font.render("Equipment:", True, (200, 200, 255))
        screen.blit(eq_title, (eq_x, eq_y))
        eq_slots = [("Main Hand", char.equipment.main_hand), ("Body", char.equipment.body), ("Accessory", char.equipment.accessory)]
        for i, (slot, item) in enumerate(eq_slots):
            item_name = item.name if item else "None"
            surf = self.font.render(f"{slot}: {item_name}", True, (220, 220, 220))
            screen.blit(surf, (eq_x, eq_y + 30 + i * 30))

        inv_y = self.rect.y + 280
        inv_title = self.font.render(f"Shared Inventory (Gold: {party.gold}, Food: {party.food}):", True, (200, 255, 200))
        screen.blit(inv_title, (self.rect.x + 20, inv_y))
        for i, item in enumerate(party.inventory[:8]):
            surf = self.small_font.render(f"- {str(item)}", True, (200, 200, 200))
            screen.blit(surf, (self.rect.x + 20, inv_y + 30 + i * 20))

    def handle_keydown(self, key):
        if key == pygame.K_1: self.char_idx = 0
        elif key == pygame.K_2: self.char_idx = 1
        elif key == pygame.K_3: self.char_idx = 2
        elif key == pygame.K_4: self.char_idx = 3
        elif key == pygame.K_5: self.char_idx = 4
        elif key == pygame.K_6: self.char_idx = 5

    def handle_click(self, pos, party: Party) -> bool:
        if not party.members: return False
        char = party.members[self.char_idx]
        if char.attribute_points <= 0: return False

        for rect, attr in self.attr_rects:
            if rect.collidepoint(pos):
                if attr == "attack": char.attack += 1
                elif attr == "defense": char.defense += 1
                elif attr == "speed": char.speed += 1
                char.attribute_points -= 1
                return True
        return False
