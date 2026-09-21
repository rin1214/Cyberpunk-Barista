"""
============================================================
CYBERPUNK CAFÉ
LOADING SCREEN
============================================================

Used for:

    Start of game
    Level 2 transition
    Level 3 transition

Music is deliberately NOT controlled here.

Therefore the background music continues playing.
============================================================
"""

import os
import pygame


class LoadingScreen:

    WIDTH = 1280
    HEIGHT = 720

    FPS = 60

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
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        screen,
    ):

        self.screen = screen

        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # PROJECT ROOT
        # ----------------------------------------------------

        self.project_root = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.mahirah_root = os.path.join(
            self.project_root,
            "assets",
            "mahirah",
        )

        self.start_root = os.path.join(
            self.mahirah_root,
            "start",
        )

        self.loading_root = os.path.join(
            self.mahirah_root,
            "loading",
        )

        # ----------------------------------------------------
        # ASSETS
        # ----------------------------------------------------

        self.background = self._load_image(
            "loading_bg.png",
            self.loading_root,
        )

        # Fallback to start background if necessary.
        if self.background is None:

            self.background = self._load_image(
                "start_bg.png",
                self.start_root,
            )

        self.logo = self._load_image(
            "logo_cyberpunk_cafe.png",
            self.start_root,
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
    # IMAGE LOADER
    # ========================================================

    def _load_image(
        self,
        filename,
        folder,
    ):

        path = os.path.join(
            folder,
            filename,
        )

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

            print(
                f"[LOADING SCREEN] "
                f"Loaded: {path}"
            )

            return image

        except (
            pygame.error,
            FileNotFoundError,
        ) as error:

            print(
                f"[LOADING SCREEN WARNING] "
                f"Could not load: {path}"
            )

            print(
                f"[LOADING SCREEN WARNING] "
                f"{error}"
            )

            return None

    # ========================================================
    # BACKGROUND
    # ========================================================

    def _draw_background(self):

        if self.background is None:

            self.screen.fill(
                (
                    18,
                    15,
                    35,
                )
            )

            return

        iw, ih = (
            self.background.get_size()
        )

        scale = max(
            self.WIDTH / float(iw),
            self.HEIGHT / float(ih),
        )

        new_size = (
            max(
                1,
                int(iw * scale),
            ),
            max(
                1,
                int(ih * scale),
            ),
        )

        image = pygame.transform.smoothscale(
            self.background,
            new_size,
        )

        x = (
            self.WIDTH
            - new_size[0]
        ) // 2

        y = (
            self.HEIGHT
            - new_size[1]
        ) // 2

        self.screen.blit(
            image,
            (
                x,
                y,
            ),
        )

        # ----------------------------------------------------
        # SOFT DARK OVERLAY
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
            430 / float(iw),
            145 / float(ih),
        )

        size = (
            max(
                1,
                int(iw * scale),
            ),
            max(
                1,
                int(ih * scale),
            ),
        )

        image = pygame.transform.smoothscale(
            self.logo,
            size,
        )

        rect = image.get_rect(
            center=(
                self.WIDTH // 2,
                105,
            )
        )

        self.screen.blit(
            image,
            rect,
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
            rect.inflate(-12, -12),
            width=1,
            border_radius=10,
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

        rendered = font.render(
            str(text),
            True,
            color,
        )

        rect = rendered.get_rect(
            center=(
                self.WIDTH // 2,
                y,
            )
        )

        self.screen.blit(
            rendered,
            rect,
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

        progress = max(
            0.0,
            min(
                1.0,
                progress,
            ),
        )

        fill_w = int(
            (w - 6)
            * progress
        )

        if fill_w > 0:

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

            highlight_w = min(
                80,
                fill_w,
            )

            highlight = pygame.Rect(
                x + 3 + fill_w - highlight_w,
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

        message = self.MESSAGES[
            index
            % len(self.MESSAGES)
        ]

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
    # RUN
    # ========================================================

    def run(
        self,
        player_name="Barista",
        level=1,
        duration=6.7,
    ):
        """
        Display the loading screen.

        Music is intentionally untouched.

        Returns:

            True  = finished
            False = player closed game
        """

        player_name = (
            str(player_name).strip()
            or "BARISTA"
        )

        try:

            level = int(level)

        except (
            TypeError,
            ValueError,
        ):

            level = 1

        level = max(
            1,
            min(
                level,
                3,
            ),
        )

        location, sector = (
            self.LEVEL_INFO[level]
        )

        print(
            "[LOADING SCREEN] "
            f"STARTING Level {level}"
        )

        print(
            "[LOADING SCREEN] "
            f"Location: {location}"
        )

        print(
            "[LOADING SCREEN] "
            f"Duration: {duration:.1f} seconds"
        )

        elapsed = 0.0

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
                        "QUIT received."
                    )

                    return False

            # ------------------------------------------------
            # PROGRESS
            # ------------------------------------------------

            progress = min(
                1.0,
                elapsed / float(duration),
            )

            smooth = (
                progress
                * progress
                * (
                    3.0
                    - 2.0 * progress
                )
            )

            index = min(
                len(self.MESSAGES) - 1,
                int(
                    progress
                    * len(self.MESSAGES)
                ),
            )

            # ------------------------------------------------
            # DRAW
            # ------------------------------------------------

            self._draw_background()

            self._draw_logo()

            self._draw_panel()

            self._text_center(
                f"WELCOME, {player_name.upper()}!",
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
                "GOOD COFFEE  ✦  BRIGHTER PEOPLE",
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
            "[LOADING SCREEN] "
            f"Level {level} loading finished."
        )

        return True