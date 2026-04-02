import pygame

# UI Theme Colors
COLOR_BG_DARK = (20, 20, 25)
COLOR_PANEL_BG = (35, 35, 45)
COLOR_FRAME_GOLD = (212, 175, 55)
COLOR_FRAME_SILVER = (192, 192, 192)
COLOR_TEXT_WHITE = (245, 245, 245)
COLOR_TEXT_GOLD = (255, 215, 0)
COLOR_HP_RED = (200, 50, 50)
COLOR_XP_GREEN = (50, 200, 50)
COLOR_AP_BLUE = (50, 100, 250)
COLOR_BUTTON_HOVER = (60, 60, 80)
COLOR_BUTTON_NORMAL = (45, 45, 60)

class UIHelper:
    @staticmethod
    def draw_frame(surface: pygame.Surface, rect: pygame.Rect, border_color=COLOR_FRAME_GOLD, bg_color=COLOR_PANEL_BG, border_width=2):
        """Draws a framed panel with a gold or silver border."""
        pygame.draw.rect(surface, bg_color, rect)
        pygame.draw.rect(surface, border_color, rect, border_width)
        # Inner thin border for extra detail
        inner_rect = rect.inflate(-border_width * 4, -border_width * 4)
        pygame.draw.rect(surface, (bg_color[0] + 10, bg_color[1] + 10, bg_color[2] + 10), inner_rect, 1)

    @staticmethod
    def draw_progress_bar(surface: pygame.Surface, x, y, width, height, current, maximum, color=COLOR_HP_RED, border_color=(255, 255, 255)):
        """Draws a progress bar with a border."""
        fill_width = int((current / maximum) * width) if maximum > 0 else 0
        fill_width = max(0, min(width, fill_width))

        bg_rect = pygame.Rect(x, y, width, height)
        fill_rect = pygame.Rect(x, y, fill_width, height)

        pygame.draw.rect(surface, (40, 40, 40), bg_rect)
        pygame.draw.rect(surface, color, fill_rect)
        pygame.draw.rect(surface, border_color, bg_rect, 1)

    @staticmethod
    def draw_button(surface: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font, is_hovered=False):
        """Draws a stylized button with a hover state."""
        color = COLOR_BUTTON_HOVER if is_hovered else COLOR_BUTTON_NORMAL
        border_color = COLOR_FRAME_GOLD if is_hovered else COLOR_FRAME_SILVER

        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, border_color, rect, 2)

        text_surf = font.render(text, True, COLOR_TEXT_WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    @staticmethod
    def render_text_wrapped(surface: pygame.Surface, text: str, pos: tuple, font: pygame.font.Font, max_width: int, color=COLOR_TEXT_WHITE):
        """Renders text with word wrapping."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if font.size(' '.join(current_line))[0] > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))

        y_offset = 0
        for line in lines:
            line_surf = font.render(line, True, color)
            surface.blit(line_surf, (pos[0], pos[1] + y_offset))
            y_offset += font.get_linesize()
        return y_offset
