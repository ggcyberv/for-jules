import pygame
import os

def generate_sprites():
    pygame.init()
    os.makedirs("data/sprites", exist_ok=True)

    # Define colors
    colors = {
        "knight": (100, 100, 255),
        "healer": (200, 255, 200),
        "orc": (50, 150, 50),
        "skeleton": (200, 200, 200),
        "wolf": (150, 75, 0),
        "bandit": (100, 50, 50),
        "slash": (255, 255, 255),
        "spark": (255, 255, 0)
    }

    size = 32
    for name, color in colors.items():
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        if name in ["slash", "spark"]:
            # Special shapes for effects
            if name == "slash":
                pygame.draw.line(surf, color, (5, 5), (25, 25), 3)
            else: # spark
                pygame.draw.circle(surf, color, (16, 16), 8)
                pygame.draw.line(surf, color, (16, 0), (16, 32), 2)
                pygame.draw.line(surf, color, (0, 16), (32, 16), 2)
        else:
            # Simple character representation: head and body
            pygame.draw.circle(surf, color, (size // 2, size // 3), size // 4)
            pygame.draw.rect(surf, color, (size // 4, size // 2, size // 2, size // 2))
            # Eyes for character types
            eye_color = (0, 0, 0)
            if name in ["orc", "wolf", "bandit"]: eye_color = (255, 0, 0)
            pygame.draw.circle(surf, eye_color, (size // 2 - 5, size // 3), 2)
            pygame.draw.circle(surf, eye_color, (size // 2 + 5, size // 3), 2)

        pygame.image.save(surf, f"data/sprites/{name}.png")

    pygame.quit()

if __name__ == "__main__":
    generate_sprites()
