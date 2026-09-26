"""
CYBERPUNK CAFÉ
LEVEL UNLOCK SCREEN

Shows the full-screen Level 2/3 unlock artwork.
"""

import os
import pygame


class LevelUnlockScreen:

    WIDTH = 1280
    HEIGHT = 720
    FPS = 60
    DISPLAY_TIME = 4.5

    LEVEL_IMAGES = {
        2: "level_2_unlock.png",
        3: "level_3_unlock.png",
    }

    def __init__(self, screen):

        self.screen = screen
        self.clock = pygame.time.Clock()

        self.project_root = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.unlock_root = os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "unlock",
        )

        self.images = {}
        self.scaled_cache = {}

        for level, filename in self.LEVEL_IMAGES.items():

            self.images[level] = self._load_image(
                filename
            )

    def _load_image(self, filename):

        path = os.path.join(
            self.unlock_root,
            filename,
        )

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

            print(
                f"[UNLOCK ASSET] Loaded: {path}"
            )

            return image

        except (
            pygame.error,
            FileNotFoundError,
        ) as error:

            print(
                "[UNLOCK ASSET ERROR]"
            )

            print(
                f"       {path}"
            )

            print(
                f"       {error}"
            )

            return None

    def _draw_image(self, image):

        if image is None:

            # A visible fallback so a missing asset can never
            # look like the screen simply failed to open.
            self.screen.fill(
                (15, 10, 30)
            )

            font = pygame.font.SysFont(
                "Consolas",
                34,
                bold=True,
            )

            text = font.render(
                "LEVEL UNLOCKED",
                True,
                (0, 225, 255),
            )

            rect = text.get_rect(
                center=(640, 340)
            )

            self.screen.blit(
                text,
                rect,
            )

            return

        if image not in self.scaled_cache:
            image_width, image_height = image.get_size()
            scale = max(
                self.WIDTH / image_width,
                self.HEIGHT / image_height,
            )
            new_size = (
                max(1, int(image_width * scale)),
                max(1, int(image_height * scale)),
            )
            scaled = pygame.transform.smoothscale(image, new_size)
            x = (self.WIDTH - new_size[0]) // 2
            y = (self.HEIGHT - new_size[1]) // 2
            self.scaled_cache[image] = (scaled, (x, y))

        scaled_img, pos = self.scaled_cache[image]
        self.screen.blit(scaled_img, pos)

    def _draw_subtle_effect(self, elapsed):

        # Very subtle scanline effect.
        lines = pygame.Surface(
            (
                self.WIDTH,
                self.HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        for y in range(
            0,
            self.HEIGHT,
            4,
        ):

            pygame.draw.line(
                lines,
                (255, 255, 255, 10),
                (0, y),
                (self.WIDTH, y),
            )

        self.screen.blit(
            lines,
            (0, 0),
        )

        glow_y = int(
            (elapsed * 35)
            % self.HEIGHT
        )

        glow = pygame.Surface(
            (
                self.WIDTH,
                35,
            ),
            pygame.SRCALPHA,
        )

        glow.fill(
            (120, 220, 255, 12)
        )

        self.screen.blit(
            glow,
            (
                0,
                glow_y - 17,
            ),
        )

    def run(
        self,
        level,
        duration=DISPLAY_TIME,
    ):
        """
        Display the unlock artwork for the requested level.

        Returns:
            True  = finished normally
            False = player closed the game
        """

        try:
            level = int(level)
        except (
            TypeError,
            ValueError,
        ):
            level = 2

        level = max(
            2,
            min(level, 3),
        )

        image = self.images.get(level)

        print(
            f"[UNLOCK SCREEN] Displaying Level {level} artwork."
        )

        if image is None:

            print(
                f"[UNLOCK SCREEN] Level {level} "
                "artwork is unavailable; showing fallback."
            )

        start_ticks = pygame.time.get_ticks()
        self.clock.tick(self.FPS)

        while True:
            elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
            if elapsed >= duration:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

            self._draw_image(image)
            self._draw_subtle_effect(elapsed)
            pygame.display.flip()
            self.clock.tick(self.FPS)

        # Ensure the final unlock frame is committed before
        # the loading screen starts.
        pygame.display.flip()

        return True
