"""
CYBERPUNK CAFÉ
LOADING SCREEN

Reusable 1280x720 loading screen for all three levels.
"""

import os
import pygame


class LoadingScreen:

    WIDTH = 1280
    HEIGHT = 720
    FPS = 60

    LEVEL_INFO = {
        1: ("BACK ALLEY KIOSK", "SECTOR 01"),
        2: ("NEON LOUNGE", "SECTOR 02"),
        3: ("CYBER PENTHOUSE", "SECTOR 03"),
    }

    MESSAGES = [
        "Initializing Café Network...",
        "Syncing Customer Database...",
        "Calibrating Drink Dispenser...",
        "Preparing Neon Menu...",
        "Warming Coffee Machines...",
        "Connecting Café Systems...",
        "Almost Ready...",
    ]

    def __init__(self, screen):

        self.screen = screen
        self.clock = pygame.time.Clock()

        self.project_root = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.start_root = os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "start",
        )

        self.loading_root = os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "loading",
        )

        self.background = self._load(
            "loading_bg.png",
            self.loading_root,
        )

        self.logo = self._load(
            "logo_cyberpunk_cafe.png",
            self.start_root,
        )

        if self.background is None:

            self.background = self._load(
                "start_bg.png",
                self.start_root,
            )

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

    def _load(self, filename, folder):

        path = os.path.join(
            folder,
            filename,
        )

        try:

            image = pygame.image.load(
                path
            ).convert_alpha()

            print(
                f"[LOADING ASSET] Loaded: {path}"
            )

            return image

        except (
            pygame.error,
            FileNotFoundError,
        ) as error:

            print(
                f"[LOADING ASSET WARNING] {path}"
            )

            print(
                f"       {error}"
            )

            return None

    def _draw_background(self):

        if self.background is None:

            self.screen.fill(
                (18, 15, 35)
            )

            return

        iw, ih = (
            self.background.get_size()
        )

        scale = max(
            self.WIDTH / iw,
            self.HEIGHT / ih,
        )

        size = (
            max(1, int(iw * scale)),
            max(1, int(ih * scale)),
        )

        image = pygame.transform.smoothscale(
            self.background,
            size,
        )

        self.screen.blit(
            image,
            (
                (self.WIDTH - size[0]) // 2,
                (self.HEIGHT - size[1]) // 2,
            ),
        )

        overlay = pygame.Surface(
            (
                self.WIDTH,
                self.HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (5, 8, 20, 35)
        )

        self.screen.blit(
            overlay,
            (0, 0),
        )

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
            max(1, int(iw * scale)),
            max(1, int(ih * scale)),
        )

        image = pygame.transform.smoothscale(
            self.logo,
            size,
        )

        self.screen.blit(
            image,
            image.get_rect(
                center=(640, 105)
            ),
        )

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

        self.screen.blit(
            surface,
            surface.get_rect(
                center=(640, y)
            ),
        )

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
            (8, 12, 28, 185)
        )

        self.screen.blit(
            panel,
            rect.topleft,
        )

        pygame.draw.rect(
            self.screen,
            (0, 220, 255),
            rect,
            width=2,
            border_radius=14,
        )

        pygame.draw.rect(
            self.screen,
            (255, 100, 200),
            rect.inflate(-12, -12),
            width=1,
            border_radius=10,
        )

    def _draw_progress(self, progress):

        x, y, w, h = (
            400,
            350,
            480,
            26,
        )

        outer = pygame.Rect(
            x, y, w, h
        )

        pygame.draw.rect(
            self.screen,
            (15, 20, 38),
            outer,
            border_radius=13,
        )

        fill_w = int(
            (w - 6)
            * max(
                0.0,
                min(1.0, progress),
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
                (255, 100, 205),
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
                (80, 225, 255),
                highlight,
                border_radius=10,
            )

        pygame.draw.rect(
            self.screen,
            (0, 225, 255),
            outer,
            width=2,
            border_radius=13,
        )

        percent = self.percent_font.render(
            f"{int(progress * 100)}%",
            True,
            (255, 255, 255),
        )

        self.screen.blit(
            percent,
            percent.get_rect(
                midleft=(900, 363)
            ),
        )

    def _draw_message(self, index):

        message = self.MESSAGES[
            index % len(self.MESSAGES)
        ]

        prefix = self.small_font.render(
            ">>",
            True,
            (255, 100, 205),
        )

        text = self.message_font.render(
            message,
            True,
            (220, 235, 255),
        )

        self.screen.blit(
            prefix,
            (410, 405),
        )

        self.screen.blit(
            text,
            (445, 403),
        )

    DEFAULT_DURATION = 5.8

    def run(
        self,
        player_name="Barista",
        level=1,
        duration=DEFAULT_DURATION,
    ):
        """
        Display the loading screen.

        Returns True when finished normally.
        Returns False if the player closes the game.
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
            min(level, 3),
        )

        location, sector = self.LEVEL_INFO[
            level
        ]

        print(
            f"[LOADING SCREEN] STARTING Level {level}"
        )

        print(
            f"[LOADING SCREEN] Location: {location}"
        )

        print(
            f"[LOADING SCREEN] Duration: {duration} seconds"
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

            progress = min(
                1.0,
                elapsed / duration,
            )

            smooth = (
                progress
                * progress
                * (3.0 - 2.0 * progress)
            )

            index = min(
                len(self.MESSAGES) - 1,
                int(
                    progress
                    * len(self.MESSAGES)
                ),
            )

            self._draw_background()
            self._draw_logo()
            self._draw_panel()

            self._text_center(
                f"WELCOME, {player_name.upper()}!",
                self.name_font,
                (255, 180, 235),
                245,
            )

            self._text_center(
                location,
                self.title_font,
                (0, 235, 255),
                285,
            )

            self._text_center(
                sector,
                self.small_font,
                (210, 220, 245),
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
                (255, 190, 235),
                565,
            )

            self._text_center(
                "Preparing your café experience...",
                self.small_font,
                (180, 205, 235),
                595,
            )

            pygame.display.flip()
            self.clock.tick(self.FPS)

        # Show full 100% progress frame before continuing
        self._draw_background()
        self._draw_logo()
        self._draw_panel()
        self._text_center(
            f"WELCOME, {player_name.upper()}!",
            self.name_font,
            (255, 180, 235),
            245,
        )
        self._text_center(
            location,
            self.title_font,
            (0, 235, 255),
            285,
        )
        self._text_center(
            sector,
            self.small_font,
            (210, 220, 245),
            315,
        )
        self._draw_progress(1.0)
        self._draw_message(len(self.MESSAGES) - 1)
        self._text_center(
            "GOOD COFFEE  ✦  BRIGHTER PEOPLE",
            self.small_font,
            (255, 190, 235),
            565,
        )
        self._text_center(
            "Preparing your café experience...",
            self.small_font,
            (180, 205, 235),
            595,
        )
        pygame.display.flip()

        print(
            f"[LOADING SCREEN] Level {level} loading finished."
        )

        return True
