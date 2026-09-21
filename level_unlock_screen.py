"""
============================================================
CYBERPUNK CAFÉ
LEVEL UNLOCK SCREEN
============================================================

PURPOSE
------------------------------------------------------------

This screen appears whenever the player naturally advances:

    Level 1 -> Level 2

or:

    Level 2 -> Level 3

The sequence is:

    GAMEPLAY
        ↓
    LEVEL UP
        ↓
    LEVEL UNLOCK SCREEN
        ↓
    LOADING SCREEN
        ↓
    NEW LEVEL GAMEPLAY


IMPORTANT
------------------------------------------------------------

This file DOES NOT start or stop music.

The game's background music must continue playing.

============================================================
"""

import os
import pygame


class LevelUnlockScreen:

    # ========================================================
    # SCREEN
    # ========================================================

    WIDTH = 1280
    HEIGHT = 720

    FPS = 60

    # How long the unlock screen stays visible.
    DISPLAY_TIME = 4.5

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        screen,
    ):

        self.screen = screen

        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Always find the project folder based on this Python
        # file instead of depending on the VS Code working
        # directory.
        # ----------------------------------------------------

        self.project_root = os.path.dirname(
            os.path.abspath(__file__)
        )

        # ----------------------------------------------------
        # UNLOCK ASSET FOLDER
        # ----------------------------------------------------

        self.unlock_root = os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "unlock",
        )

        # ----------------------------------------------------
        # FINAL UNLOCK ARTWORK
        # ----------------------------------------------------

        self.level_images = {

            2: "level_2_unlock.png",

            3: "level_3_unlock.png",

        }

        # ----------------------------------------------------
        # LOADED IMAGES
        # ----------------------------------------------------

        self.images = {}

        self._load_images()

    # ========================================================
    # LOAD IMAGES
    # ========================================================

    def _load_images(self):

        print()
        print(
            "================================================"
        )

        print(
            "[UNLOCK SCREEN] Loading level unlock artwork..."
        )

        print(
            "================================================"
        )

        for level, filename in (
            self.level_images.items()
        ):

            path = os.path.join(
                self.unlock_root,
                filename,
            )

            print(
                f"[UNLOCK SCREEN] "
                f"Level {level} asset:"
            )

            print(
                f"    {path}"
            )

            # ------------------------------------------------
            # CHECK FILE
            # ------------------------------------------------

            if not os.path.exists(path):

                print(
                    f"[UNLOCK SCREEN ERROR] "
                    f"FILE DOES NOT EXIST:"
                )

                print(
                    f"    {path}"
                )

                self.images[level] = None

                continue

            # ------------------------------------------------
            # LOAD FILE
            # ------------------------------------------------

            try:

                image = pygame.image.load(
                    path
                ).convert()

                self.images[level] = image

                print(
                    f"[UNLOCK SCREEN] "
                    f"Level {level} artwork loaded successfully."
                )

                print(
                    f"    Size: "
                    f"{image.get_width()} x "
                    f"{image.get_height()}"
                )

            except pygame.error as error:

                print(
                    f"[UNLOCK SCREEN ERROR] "
                    f"Could not load Level {level} artwork."
                )

                print(
                    f"    {error}"
                )

                self.images[level] = None

        print(
            "================================================"
        )

        print()

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    def _draw_fallback_background(
        self,
        level,
    ):
        """
        This is deliberately NOT blank.

        If the artwork fails to load, the player will still
        clearly see that the Level Unlock Screen is working.
        """

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        self.screen.fill(
            (
                8,
                10,
                28,
            )
        )

        # ----------------------------------------------------
        # LARGE CYBER GLOW
        # ----------------------------------------------------

        glow = pygame.Surface(
            (
                self.WIDTH,
                self.HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow,
            (
                0,
                220,
                255,
                35,
            ),
            (
                self.WIDTH // 2,
                self.HEIGHT // 2,
            ),
            320,
        )

        pygame.draw.circle(
            glow,
            (
                255,
                80,
                200,
                25,
            ),
            (
                self.WIDTH // 2,
                self.HEIGHT // 2,
            ),
            220,
        )

        self.screen.blit(
            glow,
            (
                0,
                0,
            ),
        )

        # ----------------------------------------------------
        # PANEL
        # ----------------------------------------------------

        panel = pygame.Rect(
            220,
            145,
            840,
            430,
        )

        panel_surface = pygame.Surface(
            panel.size,
            pygame.SRCALPHA,
        )

        panel_surface.fill(
            (
                12,
                16,
                38,
                235,
            )
        )

        self.screen.blit(
            panel_surface,
            panel.topleft,
        )

        pygame.draw.rect(
            self.screen,
            (
                0,
                225,
                255,
            ),
            panel,
            3,
            border_radius=20,
        )

        pygame.draw.rect(
            self.screen,
            (
                255,
                90,
                205,
            ),
            panel.inflate(
                -14,
                -14,
            ),
            1,
            border_radius=16,
        )

        # ----------------------------------------------------
        # FONTS
        # ----------------------------------------------------

        title_font = pygame.font.SysFont(
            "Consolas",
            48,
            bold=True,
        )

        level_font = pygame.font.SysFont(
            "Consolas",
            88,
            bold=True,
        )

        location_font = pygame.font.SysFont(
            "Consolas",
            34,
            bold=True,
        )

        small_font = pygame.font.SysFont(
            "Consolas",
            20,
            bold=True,
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = title_font.render(
            "LEVEL UNLOCKED",
            True,
            (
                255,
                175,
                235,
            ),
        )

        title_rect = title.get_rect(
            center=(
                self.WIDTH // 2,
                220,
            )
        )

        self.screen.blit(
            title,
            title_rect,
        )

        # ----------------------------------------------------
        # LEVEL NUMBER
        # ----------------------------------------------------

        level_text = level_font.render(
            f"LEVEL {level}",
            True,
            (
                0,
                235,
                255,
            ),
        )

        level_rect = level_text.get_rect(
            center=(
                self.WIDTH // 2,
                335,
            )
        )

        self.screen.blit(
            level_text,
            level_rect,
        )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        locations = {

            2: "NEON LOUNGE",

            3: "CYBER PENTHOUSE",

        }

        location = locations.get(
            level,
            "NEW CAFÉ AREA",
        )

        location_text = location_font.render(
            location,
            True,
            (
                255,
                255,
                255,
            ),
        )

        location_rect = location_text.get_rect(
            center=(
                self.WIDTH // 2,
                425,
            )
        )

        self.screen.blit(
            location_text,
            location_rect,
        )

        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        message = small_font.render(
            "Preparing your new café experience...",
            True,
            (
                190,
                215,
                245,
            ),
        )

        message_rect = message.get_rect(
            center=(
                self.WIDTH // 2,
                490,
            )
        )

        self.screen.blit(
            message,
            message_rect,
        )

    # ========================================================
    # DRAW IMAGE
    # ========================================================

    def _draw_image(
        self,
        image,
        level,
    ):
        """
        Draw the actual unlock artwork.

        If the artwork cannot be loaded, the visible fallback
        screen is drawn instead.
        """

        if image is None:

            self._draw_fallback_background(
                level
            )

            return

        # ----------------------------------------------------
        # ORIGINAL SIZE
        # ----------------------------------------------------

        image_width = image.get_width()

        image_height = image.get_height()

        # ----------------------------------------------------
        # SCALE TO COVER 1280 x 720
        # ----------------------------------------------------

        scale = max(

            self.WIDTH
            / float(image_width),

            self.HEIGHT
            / float(image_height),

        )

        new_width = max(
            1,
            int(
                image_width
                * scale
            ),
        )

        new_height = max(
            1,
            int(
                image_height
                * scale
            ),
        )

        scaled = pygame.transform.smoothscale(
            image,
            (
                new_width,
                new_height,
            ),
        )

        # ----------------------------------------------------
        # CENTER
        # ----------------------------------------------------

        x = (
            self.WIDTH
            - new_width
        ) // 2

        y = (
            self.HEIGHT
            - new_height
        ) // 2

        self.screen.blit(
            scaled,
            (
                x,
                y,
            ),
        )

    # ========================================================
    # VISUAL EFFECT
    # ========================================================

    def _draw_effect(
        self,
        elapsed,
    ):
        """
        Adds a very subtle cyberpunk scanline effect.
        """

        overlay = pygame.Surface(
            (
                self.WIDTH,
                self.HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        # ----------------------------------------------------
        # SCANLINES
        # ----------------------------------------------------

        for y in range(
            0,
            self.HEIGHT,
            6,
        ):

            pygame.draw.line(
                overlay,
                (
                    255,
                    255,
                    255,
                    7,
                ),
                (
                    0,
                    y,
                ),
                (
                    self.WIDTH,
                    y,
                ),
            )

        self.screen.blit(
            overlay,
            (
                0,
                0,
            ),
        )

        # ----------------------------------------------------
        # MOVING NEON LIGHT
        # ----------------------------------------------------

        glow_height = 50

        glow_y = int(
            (
                elapsed
                * 130
            )
            % (
                self.HEIGHT
                + glow_height
            )
        )

        glow = pygame.Surface(
            (
                self.WIDTH,
                glow_height,
            ),
            pygame.SRCALPHA,
        )

        glow.fill(
            (
                0,
                220,
                255,
                10,
            )
        )

        self.screen.blit(
            glow,
            (
                0,
                glow_y
                - glow_height,
            ),
        )

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        level,
        duration=None,
    ):
        """
        Display the Level Unlock Screen.

        This function temporarily takes control of the
        display until the celebration is complete.

        IMPORTANT:

        Music is NOT changed here.
        """

        # ----------------------------------------------------
        # DEFAULT DURATION
        # ----------------------------------------------------

        if duration is None:

            duration = self.DISPLAY_TIME

        # ----------------------------------------------------
        # SAFE LEVEL
        # ----------------------------------------------------

        try:

            level = int(level)

        except (
            TypeError,
            ValueError,
        ):

            print(
                "[UNLOCK SCREEN ERROR] "
                "Invalid level."
            )

            return True

        # ----------------------------------------------------
        # LEVEL 1 DOES NOT NEED UNLOCK ART
        # ----------------------------------------------------

        if level <= 1:

            return True

        # ----------------------------------------------------
        # NEVER ALLOW LEVEL ABOVE 3
        # ----------------------------------------------------

        level = min(
            level,
            3,
        )

        print()
        print(
            "================================================"
        )

        print(
            f"[LEVEL TRANSITION] "
            f"STARTING LEVEL {level} UNLOCK SCREEN"
        )

        print(
            f"[LEVEL TRANSITION] "
            f"Duration: {duration:.1f} seconds"
        )

        print(
            "================================================"
        )

        # ----------------------------------------------------
        # GET IMAGE
        # ----------------------------------------------------

        image = self.images.get(
            level
        )

        if image is None:

            print(
                f"[UNLOCK SCREEN] "
                f"No artwork loaded for Level {level}."
            )

            print(
                "[UNLOCK SCREEN] "
                "Showing visible fallback screen."
            )

        else:

            print(
                f"[UNLOCK SCREEN] "
                f"Displaying Level {level} artwork."
            )

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        elapsed = 0.0

        # ----------------------------------------------------
        # BLOCK NORMAL GAME LOOP
        # ----------------------------------------------------

        while elapsed < duration:

            dt = (
                self.clock.tick(
                    self.FPS
                )
                / 1000.0
            )

            elapsed += dt

            # ------------------------------------------------
            # EVENTS
            # ------------------------------------------------

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    print(
                        "[UNLOCK SCREEN] "
                        "QUIT received."
                    )

                    return False

            # ------------------------------------------------
            # DRAW
            # ------------------------------------------------

            self._draw_image(
                image,
                level,
            )

            self._draw_effect(
                elapsed,
            )

            # ------------------------------------------------
            # DISPLAY
            # ------------------------------------------------

            pygame.display.flip()

        # ----------------------------------------------------
        # FINISHED
        # ----------------------------------------------------

        print(
            f"[LEVEL TRANSITION] "
            f"LEVEL {level} UNLOCK SCREEN FINISHED"
        )

        print()

        return True


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    pygame.init()

    screen = pygame.display.set_mode(
        (
            1280,
            720,
        )
    )

    pygame.display.set_caption(
        "Cyberpunk Café - Level Unlock Test"
    )

    unlock_screen = LevelUnlockScreen(
        screen
    )

    # Test Level 2.
    unlock_screen.run(
        level=2,
        duration=4.5,
    )

    pygame.quit()