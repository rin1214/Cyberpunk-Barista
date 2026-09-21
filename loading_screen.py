import os
import pygame


class LoadingScreen:
    """
    Cyberpunk Café reusable 1280x720 loading screen.
    """

    WIDTH = 1280
    HEIGHT = 720

    FPS = 60

    # ========================================================
    # PROJECT PATH
    # ========================================================

    PROJECT_ROOT = os.path.dirname(
        os.path.abspath(__file__)
    )

    MAHIRAH_ROOT = os.path.join(
        PROJECT_ROOT,
        "assets",
        "mahirah",
    )

    START_ROOT = os.path.join(
        MAHIRAH_ROOT,
        "start",
    )

    LOADING_ROOT = os.path.join(
        MAHIRAH_ROOT,
        "loading",
    )

    # ========================================================
    # LEVEL INFORMATION
    # ========================================================

    LEVEL_INFO = {

        1: (
            "BACK ALLEY KIOSK",
            "SECTOR 01",
        ),

        2: (
            "NEON LOUNGE",
            "SECTOR 02",
        ),

        3: (
            "CYBER PENTHOUSE",
            "SECTOR 03",
        ),
    }

    # ========================================================
    # LOADING MESSAGES
    # ========================================================

    MESSAGES = [

        "Initializing Café Network...",

        "Syncing Customer Database...",

        "Calibrating Drink Dispenser...",

        "Preparing Neon Menu...",

        "Warming Coffee Machines...",

        "Connecting Café Systems...",

        "Almost Ready...",
    ]

    # ========================================================
    # INITIALISATION
    # ========================================================

    def __init__(
        self,
        screen,
    ):

        self.screen = screen

        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # LOAD BACKGROUND
        # ----------------------------------------------------

        self.background = self._load(
            "loading_bg.png",
            self.LOADING_ROOT,
        )

        # ----------------------------------------------------
        # LOAD LOGO
        # ----------------------------------------------------

        self.logo = self._load(
            "logo_cyberpunk_cafe.png",
            self.START_ROOT,
        )

        # ----------------------------------------------------
        # FALLBACK BACKGROUND
        # ----------------------------------------------------

        if self.background is None:

            self.background = self._load(
                "start_bg.png",
                self.START_ROOT,
            )

        # ----------------------------------------------------
        # FONTS
        # ----------------------------------------------------

        self.title_font = pygame.font.SysFont(
            "Consolas",
            30,
            bold=True,
        )

        self.name_font = pygame.font.SysFont(
            "Consolas",
            25,
            bold=True,
        )

        self.message_font = pygame.font.SysFont(
            "Consolas",
            19,
            bold=True,
        )

        self.small_font = pygame.font.SysFont(
            "Consolas",
            16,
        )

        self.percent_font = pygame.font.SysFont(
            "Consolas",
            24,
            bold=True,
        )

    # ========================================================
    # LOAD ASSET
    # ========================================================

    def _load(
        self,
        filename,
        folder,
    ):
        """
        Load an image using an absolute project path.
        """

        path = os.path.join(
            folder,
            filename,
        )

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

            print(
                "[LOADING ASSET] Loaded:"
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
                "[LOADING ASSET WARNING]"
            )

            print(
                f"    Could not load: {path}"
            )

            print(
                f"    Reason: {error}"
            )

            return None

    # ========================================================
    # BACKGROUND
    # ========================================================

    def _draw_background(self):
        """
        Draw the loading background.
        """

        if self.background is None:

            self.screen.fill(
                (
                    18,
                    15,
                    35,
                )
            )

            return

        # ----------------------------------------------------
        # ORIGINAL SIZE
        # ----------------------------------------------------

        iw, ih = (
            self.background.get_size()
        )

        # ----------------------------------------------------
        # SCALE TO FILL SCREEN
        # ----------------------------------------------------

        scale = max(

            self.WIDTH / iw,

            self.HEIGHT / ih,
        )

        size = (

            max(
                1,
                int(
                    iw * scale
                ),
            ),

            max(
                1,
                int(
                    ih * scale
                ),
            ),
        )

        image = pygame.transform.smoothscale(
            self.background,
            size,
        )

        # ----------------------------------------------------
        # CENTER
        # ----------------------------------------------------

        self.screen.blit(

            image,

            (
                (
                    self.WIDTH
                    - size[0]
                ) // 2,

                (
                    self.HEIGHT
                    - size[1]
                ) // 2,
            ),
        )

        # ----------------------------------------------------
        # SUBTLE OVERLAY
        # ----------------------------------------------------

        overlay = pygame.Surface(
            (
                self.WIDTH,
                self.HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                5,
                8,
                20,
                35,
            )
        )

        self.screen.blit(
            overlay,
            (
                0,
                0,
            ),
        )

    # ========================================================
    # LOGO
    # ========================================================

    def _draw_logo(self):

        if self.logo is None:

            return

        iw, ih = (
            self.logo.get_size()
        )

        scale = min(

            430 / iw,

            145 / ih,
        )

        size = (

            max(
                1,
                int(
                    iw * scale
                ),
            ),

            max(
                1,
                int(
                    ih * scale
                ),
            ),
        )

        image = pygame.transform.smoothscale(
            self.logo,
            size,
        )

        self.screen.blit(

            image,

            image.get_rect(
                center=(
                    640,
                    105,
                )
            ),
        )

    # ========================================================
    # PANEL
    # ========================================================

    def _draw_panel(self):

        rect = pygame.Rect(
            315,
            185,
            650,
            430,
        )

        panel = pygame.Surface(
            rect.size,
            pygame.SRCALPHA,
        )

        panel.fill(
            (
                8,
                12,
                28,
                185,
            )
        )

        self.screen.blit(
            panel,
            rect.topleft,
        )

        pygame.draw.rect(

            self.screen,

            (
                0,
                220,
                255,
            ),

            rect,

            width=2,

            border_radius=14,
        )

        pygame.draw.rect(

            self.screen,

            (
                255,
                100,
                200,
            ),

            rect.inflate(
                -12,
                -12,
            ),

            width=1,

            border_radius=10,
        )

    # ========================================================
    # PROGRESS BAR
    # ========================================================

    def _draw_progress(
        self,
        progress,
    ):

        x = 400
        y = 350
        w = 480
        h = 26

        outer = pygame.Rect(
            x,
            y,
            w,
            h,
        )

        # ----------------------------------------------------
        # BAR BACKGROUND
        # ----------------------------------------------------

        pygame.draw.rect(

            self.screen,

            (
                15,
                20,
                38,
            ),

            outer,

            border_radius=13,
        )

        # ----------------------------------------------------
        # FILL
        # ----------------------------------------------------

        fill_w = int(

            (
                w - 6
            )

            *

            max(
                0.0,
                min(
                    1.0,
                    progress,
                ),
            )
        )

        if fill_w:

            fill = pygame.Rect(

                x + 3,

                y + 3,

                fill_w,

                h - 6,
            )

            pygame.draw.rect(

                self.screen,

                (
                    255,
                    100,
                    205,
                ),

                fill,

                border_radius=10,
            )

            # -----------------------------------------------
            # HIGHLIGHT
            # -----------------------------------------------

            highlight_w = min(
                80,
                fill_w,
            )

            highlight = pygame.Rect(

                x + 3
                + fill_w
                - highlight_w,

                y + 3,

                highlight_w,

                h - 6,
            )

            pygame.draw.rect(

                self.screen,

                (
                    80,
                    225,
                    255,
                ),

                highlight,

                border_radius=10,
            )

        # ----------------------------------------------------
        # OUTLINE
        # ----------------------------------------------------

        pygame.draw.rect(

            self.screen,

            (
                0,
                225,
                255,
            ),

            outer,

            width=2,

            border_radius=13,
        )

        # ----------------------------------------------------
        # PERCENTAGE
        # ----------------------------------------------------

        percent = self.percent_font.render(

            f"{int(progress * 100)}%",

            True,

            (
                255,
                255,
                255,
            ),
        )

        self.screen.blit(

            percent,

            percent.get_rect(
                midleft=(
                    900,
                    363,
                )
            ),
        )

    # ========================================================
    # MESSAGE
    # ========================================================

    def _draw_message(
        self,
        index,
    ):

        message = (
            self.MESSAGES[
                index
                % len(
                    self.MESSAGES
                )
            ]
        )

        prefix = self.small_font.render(

            ">>",

            True,

            (
                255,
                100,
                205,
            ),
        )

        text = self.message_font.render(

            message,

            True,

            (
                220,
                235,
                255,
            ),
        )

        self.screen.blit(
            prefix,
            (
                410,
                405,
            ),
        )

        self.screen.blit(
            text,
            (
                445,
                403,
            ),
        )

    # ========================================================
    # CENTER TEXT
    # ========================================================

    def _text_center(
        self,
        text,
        font,
        color,
        y,
    ):

        surface = font.render(
            text,
            True,
            color,
        )

        rect = surface.get_rect(
            center=(
                self.WIDTH // 2,
                y,
            )
        )

        self.screen.blit(
            surface,
            rect,
        )

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        player_name="Barista",
        level=1,
        duration=3.2,
    ):
        """
        Display the loading screen.

        Returns:

            True
                Loading finished.

            False
                Game was closed.
        """

        player_name = (
            str(
                player_name
            ).strip()
            or "BARISTA"
        )

        # ----------------------------------------------------
        # VALID LEVEL
        # ----------------------------------------------------

        try:

            level = int(
                level
            )

        except (
            TypeError,
            ValueError,
        ):

            level = 1

        if level not in self.LEVEL_INFO:

            level = 1

        location, sector = (
            self.LEVEL_INFO[
                level
            ]
        )

        # ----------------------------------------------------
        # DEBUG OUTPUT
        # ----------------------------------------------------

        print(
            "========================================"
        )

        print(
            "[LOADING SCREEN]"
        )

        print(
            f"Player: {player_name}"
        )

        print(
            f"Level: {level}"
        )

        print(
            f"Location: {location}"
        )

        print(
            f"Duration: {duration}s"
        )

        print(
            "========================================"
        )

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        elapsed = 0.0

        # ====================================================
        # LOOP
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
                        "[LOADING SCREEN] "
                        "Game closed."
                    )

                    return False

            # ------------------------------------------------
            # PROGRESS
            # ------------------------------------------------

            progress = min(
                1.0,
                elapsed / duration,
            )

            smooth = (
                progress
                * progress
                * (
                    3.0
                    - 2.0
                    * progress
                )
            )

            index = min(

                len(
                    self.MESSAGES
                ) - 1,

                int(
                    progress
                    * len(
                        self.MESSAGES
                    )
                ),
            )

            # ------------------------------------------------
            # DRAW
            # ------------------------------------------------

            self._draw_background()

            self._draw_logo()

            self._draw_panel()

            self._text_center(

                f"WELCOME, "
                f"{player_name.upper()}!",

                self.name_font,

                (
                    255,
                    180,
                    235,
                ),

                245,
            )

            self._text_center(

                location,

                self.title_font,

                (
                    0,
                    235,
                    255,
                ),

                285,
            )

            self._text_center(

                sector,

                self.small_font,

                (
                    210,
                    220,
                    245,
                ),

                315,
            )

            self._draw_progress(
                smooth
            )

            self._draw_message(
                index
            )

            self._text_center(

                "GOOD COFFEE  ✦  "
                "BRIGHTER PEOPLE",

                self.small_font,

                (
                    255,
                    190,
                    235,
                ),

                565,
            )

            self._text_center(

                "Preparing your café experience...",

                self.small_font,

                (
                    180,
                    205,
                    235,
                ),

                595,
            )

            pygame.display.flip()

        print(
            "[LOADING SCREEN] Finished."
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
        "Cyberpunk Café - Loading Screen"
    )

    LoadingScreen(
        screen
    ).run(
        "Mahirah",
        level=2,
        duration=6.0,
    )

    pygame.quit()