import os
import pygame


class LevelUnlockScreen:
    """
    Cyberpunk Café level-unlock celebration screen.

    This screen is shown AFTER the player actually
    reaches a new level.

    Level 2:
        Neon Lounge

    Level 3:
        Cyber Penthouse
    """

    WIDTH = 1280
    HEIGHT = 720
    FPS = 60

    DISPLAY_TIME = 4.5

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Build the asset path from the Python file's own folder.
    #
    # This prevents the screen from breaking when VS Code
    # starts the game from a different working directory.
    # --------------------------------------------------------

    PROJECT_ROOT = os.path.dirname(
        os.path.abspath(__file__)
    )

    UNLOCK_ROOT = os.path.join(
        PROJECT_ROOT,
        "assets",
        "mahirah",
        "unlock",
    )

    LEVEL_IMAGES = {

        2: "level_2_unlock.png",

        3: "level_3_unlock.png",
    }

    def __init__(
        self,
        screen,
    ):

        self.screen = screen

        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # LOAD ALL UNLOCK IMAGES
        # ----------------------------------------------------

        self.images = {}

        for level, filename in self.LEVEL_IMAGES.items():

            self.images[level] = (
                self._load_image(
                    filename
                )
            )

    # ========================================================
    # LOAD IMAGE
    # ========================================================

    def _load_image(
        self,
        filename,
    ):
        """
        Load an unlock image using an absolute project path.
        """

        path = os.path.join(
            self.UNLOCK_ROOT,
            filename,
        )

        try:

            image = pygame.image.load(
                path
            ).convert()

            print(
                "[UNLOCK ASSET] Loaded:"
            )

            print(
                f"    {path}"
            )

            print(
                f"    Size: {image.get_size()}"
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
                f"    Could not load: {path}"
            )

            print(
                f"    Reason: {error}"
            )

            return None

    # ========================================================
    # DRAW IMAGE
    # ========================================================

    def _draw_image(
        self,
        image,
    ):
        """
        Draw the unlock artwork while preserving
        its aspect ratio.
        """

        # ----------------------------------------------------
        # IMAGE MISSING
        # ----------------------------------------------------

        if image is None:

            self.screen.fill(
                (
                    15,
                    10,
                    30,
                )
            )

            return

        # ----------------------------------------------------
        # ORIGINAL SIZE
        # ----------------------------------------------------

        image_width, image_height = (
            image.get_size()
        )

        # ----------------------------------------------------
        # SCALE TO FILL 1280x720
        # ----------------------------------------------------

        scale = max(

            self.WIDTH / image_width,

            self.HEIGHT / image_height,
        )

        new_size = (

            max(
                1,
                int(
                    image_width * scale
                ),
            ),

            max(
                1,
                int(
                    image_height * scale
                ),
            ),
        )

        scaled = pygame.transform.smoothscale(
            image,
            new_size,
        )

        # ----------------------------------------------------
        # CENTER
        # ----------------------------------------------------

        x = (
            self.WIDTH
            - new_size[0]
        ) // 2

        y = (
            self.HEIGHT
            - new_size[1]
        ) // 2

        self.screen.blit(
            scaled,
            (
                x,
                y,
            ),
        )

    # ========================================================
    # EFFECT
    # ========================================================

    def _draw_subtle_effect(
        self,
        elapsed,
    ):
        """
        Add a very subtle cyberpunk scanline effect.
        """

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

                (
                    255,
                    255,
                    255,
                    10,
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
            lines,
            (
                0,
                0,
            ),
        )

        # ----------------------------------------------------
        # MOVING GLOW
        # ----------------------------------------------------

        glow_y = int(
            (
                elapsed
                * 35
            )
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
            (
                120,
                220,
                255,
                12,
            )
        )

        self.screen.blit(
            glow,
            (
                0,
                glow_y - 17,
            ),
        )

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        level,
        duration=DISPLAY_TIME,
    ):
        """
        Show the unlock screen.

        Returns:

            True
                Screen finished normally.

            False
                Player closed the game.
        """

        # ----------------------------------------------------
        # SAFETY
        # ----------------------------------------------------

        try:

            level = int(
                level
            )

        except (
            TypeError,
            ValueError,
        ):

            print(
                "[UNLOCK SCREEN] "
                "Invalid level."
            )

            return True

        # ----------------------------------------------------
        # LEVEL 1 HAS NO UNLOCK SCREEN
        # ----------------------------------------------------

        if level == 1:

            print(
                "[UNLOCK SCREEN] "
                "Level 1 does not require an unlock screen."
            )

            return True

        # ----------------------------------------------------
        # CHECK IMAGE EXISTS
        # ----------------------------------------------------

        if level not in self.images:

            print(
                "[UNLOCK SCREEN] "
                f"No artwork configured for Level {level}."
            )

            return True

        image = self.images[level]

        # ----------------------------------------------------
        # START TIMER
        # ----------------------------------------------------

        elapsed = 0.0

        print(
            "========================================"
        )

        print(
            "[UNLOCK SCREEN]"
        )

        print(
            f"Showing Level {level} unlock screen."
        )

        print(
            f"Artwork loaded: {image is not None}"
        )

        print(
            "========================================"
        )

        # ====================================================
        # SCREEN LOOP
        # ====================================================

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
                        "Game closed."
                    )

                    return False

            # ------------------------------------------------
            # DRAW
            # ------------------------------------------------

            self._draw_image(
                image
            )

            self._draw_subtle_effect(
                elapsed
            )

            pygame.display.flip()

        print(
            "[UNLOCK SCREEN] Finished."
        )

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
        "Cyberpunk Café - Level Unlock Screen"
    )

    unlock_screen = LevelUnlockScreen(
        screen
    )

    unlock_screen.run(
        level=2,
        duration=4.5,
    )

    pygame.quit()