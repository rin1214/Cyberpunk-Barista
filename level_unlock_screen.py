import os
import pygame


class LevelUnlockScreen:
    """Cyberpunk Cafe level-unlock celebration screen."""

    WIDTH = 1280
    HEIGHT = 720
    FPS = 60
    DISPLAY_TIME = 4.0

    UNLOCK_ROOT = os.path.join("assets", "mahirah", "unlock")

    LEVEL_IMAGES = {
        2: "level_2_unlock.png",
        3: "level_3_unlock.png",
    }

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.images = {
            level: self._load_image(filename)
            for level, filename in self.LEVEL_IMAGES.items()
        }

    def _load_image(self, filename):
        path = os.path.join(self.UNLOCK_ROOT, filename)

        try:
            image = pygame.image.load(path).convert()
            print(f"[UNLOCK ASSET] Loaded: {path}")
            return image
        except (pygame.error, FileNotFoundError) as e:
            print(f"[UNLOCK ASSET WARNING] {path} ({e})")
            return None

    def _draw_image(self, image):
        if image is None:
            self.screen.fill((15, 10, 30))
            return

        image_width, image_height = image.get_size()

        # Fill the 1280x720 screen while preserving aspect ratio.
        scale = max(
            self.WIDTH / image_width,
            self.HEIGHT / image_height
        )

        new_size = (
            max(1, int(image_width * scale)),
            max(1, int(image_height * scale))
        )

        scaled = pygame.transform.smoothscale(image, new_size)

        x = (self.WIDTH - new_size[0]) // 2
        y = (self.HEIGHT - new_size[1]) // 2

        self.screen.blit(scaled, (x, y))

    def _draw_subtle_effect(self, elapsed):
        """Very subtle scanline/glow effect; no extra text or timer."""
        lines = pygame.Surface(
            (self.WIDTH, self.HEIGHT),
            pygame.SRCALPHA
        )

        for y in range(0, self.HEIGHT, 4):
            pygame.draw.line(
                lines,
                (255, 255, 255, 10),
                (0, y),
                (self.WIDTH, y)
            )

        self.screen.blit(lines, (0, 0))

        glow_y = int((elapsed * 35) % self.HEIGHT)

        glow = pygame.Surface(
            (self.WIDTH, 35),
            pygame.SRCALPHA
        )
        glow.fill((120, 220, 255, 12))

        self.screen.blit(glow, (0, glow_y - 17))

    def run(self, level, duration=DISPLAY_TIME):
        """
        Show the unlock artwork for the requested level.

        Returns True when finished normally.
        Returns False if the player closes the game.
        """

        if level not in self.images:
            print(
                f"[UNLOCK SCREEN] No unlock artwork for Level {level}."
            )
            return True

        image = self.images[level]
        elapsed = 0.0

        while elapsed < duration:
            dt = self.clock.tick(self.FPS) / 1000.0
            elapsed += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

            self._draw_image(image)
            self._draw_subtle_effect(elapsed)

            pygame.display.flip()

        return True


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption(
        "Cyberpunk Cafe - Level Unlock Screen"
    )

    unlock_screen = LevelUnlockScreen(screen)

    # Standalone test: Level 2.
    unlock_screen.run(level=2, duration=4.5)

    pygame.quit()
