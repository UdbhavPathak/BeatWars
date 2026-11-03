import pygame
import math
pygame.init()


def draw_minimap(self):

    # Minimap dimensions
    map_width = 240
    map_height = 135
    padding = 15

    # Scale world coordinates to minimap coordinates
    scale_x = map_width / self.window.get_width()
    scale_y = map_height / self.window.get_height()

    # Create minimap surface
    minimap = pygame.Surface(
        (map_width, map_height), pygame.SRCALPHA
    )

    minimap.fill((10, 15, 25, 210))

    # Draw subtle grid
    for x in range(0, map_width, 30):
        pygame.draw.line(
            minimap, (35, 45, 60, 150),
            (x, 0), (x, map_height), 1
        )

    for y in range(0, map_height, 30):
        pygame.draw.line(
            minimap, (35, 45, 60, 150),
            (0, y), (map_width, y), 1
        )

    # Draw enemies / asteroids
    for asteroid in self.asteroids:

        if not asteroid.alive:
            continue

        x = int(asteroid.rect.centerx * scale_x)
        y = int(asteroid.rect.centery * scale_y)

        pygame.draw.circle(
            minimap,
            (255, 65, 65),
            (x, y),
            3
        )

    # Player position on minimap
    px = self.player.rect.centerx * scale_x
    py = self.player.rect.centery * scale_y

    # Triangle pointing in player's current direction
    angle = math.radians(self.player.angle)

    tip = (
        px + 7 * math.cos(angle),
        py + 7 * math.sin(angle)
    )

    left = (
        px + 5 * math.cos(angle + 2.5),
        py + 5 * math.sin(angle + 2.5)
    )

    right = (
        px + 5 * math.cos(angle - 2.5),
        py + 5 * math.sin(angle - 2.5)
    )

    pygame.draw.polygon(
        minimap,
        (50, 255, 120),
        [tip, left, right]
    )

    # Minimap border
    pygame.draw.rect(
        minimap,
        (100, 120, 145),
        minimap.get_rect(),
        1
    )

    # Position minimap at top-right of main display
    map_x = self.size[0] - map_width - padding
    map_y = padding

    self.screen.blit(minimap, (map_x, map_y))
