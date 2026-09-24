"""
============================================================
CYBERPUNK CAFÉ
POLISHED ANIMATED GAME END SCREEN
============================================================

Assets:

assets/
└── mahirah/
    └── end_game/
        ├── end_game_background.png
        └── cat_wave/
            ├── 01.png
            ├── 02.png
            ├── 03.png
            ├── 04.png
            ├── 05.png
            ├── 06.png
            ├── 07.png
            └── 08.png

Fonts:

assets/fonts/
    Any .ttf or .otf font

The screen automatically searches assets/fonts for a font.

============================================================
"""

import math
import os
import pygame


# ============================================================
# GAME END SCREEN
# ============================================================

class GameEndScreen:

    # ========================================================
    # INITIALISE
    # ========================================================

    def __init__(
        self,
        screen,
        project_root=None,
    ):

        self.screen = screen

        self.width = screen.get_width()
        self.height = screen.get_height()

        # ----------------------------------------------------
        # PROJECT ROOT
        # ----------------------------------------------------

        if project_root is not None:

            self.project_root = project_root

        else:

            self.project_root = os.path.dirname(
                os.path.abspath(__file__)
            )

        # ----------------------------------------------------
        # CLOCK
        # ----------------------------------------------------

        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.running = True
        self.result = None

        self.phase = 0

        self.phase_timer = 0.0

        self.elapsed = 0.0

        # ====================================================
        # FINAL PLAYER INFORMATION
        # ====================================================

        self.player_name = "BARISTA"

        self.final_level = 3

        self.successful_drinks = 21

        self.final_xp = 0

        self.final_credits = 0

        # ====================================================
        # BACKGROUND
        # ====================================================

        self.background = None

        # ====================================================
        # CAT
        # ====================================================

        self.cat_frames = []

        self.cat_frame_index = 0

        self.cat_frame_timer = 0.0

        # 0.10 = smooth wave.
        self.cat_frame_speed = 0.10

        self.cat_size = (
            330,
            330,
        )

        self.cat_position = (
            270,
            430,
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        self.play_again_rect = pygame.Rect(
            285,
            625,
            310,
            58,
        )

        self.main_menu_rect = pygame.Rect(
            685,
            625,
            310,
            58,
        )

        # ====================================================
        # FONT SYSTEM
        # ====================================================

        self.font_path = self.find_game_font()

        # Font sizes.

        self.font_title = self.load_font(
            50
        )

        self.font_large = self.load_font(
            32
        )

        self.font_medium = self.load_font(
            25
        )

        self.font_small = self.load_font(
            19
        )

        self.font_button = self.load_font(
            22
        )

        self.font_stat = self.load_font(
            23
        )

        # ====================================================
        # COLOURS
        # ====================================================

        self.WHITE = (
            248,
            250,
            255,
        )

        self.SOFT_WHITE = (
            225,
            230,
            242,
        )

        self.CYAN = (
            75,
            225,
            255,
        )

        self.BRIGHT_CYAN = (
            125,
            240,
            255,
        )

        self.PINK = (
            255,
            105,
            215,
        )

        self.PURPLE = (
            190,
            135,
            255,
        )

        self.GOLD = (
            255,
            220,
            110,
        )

        self.GREY = (
            180,
            188,
            210,
        )

        self.DARK = (
            8,
            10,
            25,
        )

        self.PANEL = (
            11,
            15,
            35,
        )

        self.PANEL_LIGHT = (
            21,
            25,
            53,
        )

        # ====================================================
        # LOAD ASSETS
        # ====================================================

        self.load_assets()

    # ========================================================
    # FIND PROJECT FONT
    # ========================================================

    def find_game_font(self):

        font_folder = os.path.join(
            self.project_root,
            "assets",
            "fonts",
        )

        if not os.path.isdir(
            font_folder
        ):

            print(
                "[END SCREEN] Font folder not found."
            )

            return None

        font_files = []

        for root, _, files in os.walk(
            font_folder
        ):

            for filename in files:

                if filename.lower().endswith(
                    (
                        ".ttf",
                        ".otf",
                    )
                ):

                    font_files.append(
                        os.path.join(
                            root,
                            filename,
                        )
                    )

        if not font_files:

            print(
                "[END SCREEN] No custom font found."
            )

            return None

        # ----------------------------------------------------
        # PREFERRED CYBERPUNK / FUTURISTIC FONT NAMES
        # ----------------------------------------------------

        preferred_words = (
            "cyber",
            "tech",
            "orbit",
            "rajdhani",
            "audiowide",
            "exo",
            "neuropol",
            "quantum",
            "future",
            "space",
            "electro",
        )

        for path in font_files:

            filename = os.path.basename(
                path
            ).lower()

            for word in preferred_words:

                if word in filename:

                    print(
                        "[END SCREEN] Using font:",
                        path,
                    )

                    return path

        # ----------------------------------------------------
        # OTHERWISE USE FIRST PROJECT FONT
        # ----------------------------------------------------

        font_files.sort()

        print(
            "[END SCREEN] Using project font:",
            font_files[0],
        )

        return font_files[0]

    # ========================================================
    # LOAD FONT
    # ========================================================

    def load_font(
        self,
        size,
    ):

        if self.font_path is not None:

            try:

                return pygame.font.Font(
                    self.font_path,
                    size,
                )

            except pygame.error as error:

                print(
                    "[END SCREEN] Font error:",
                    error,
                )

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        return pygame.font.SysFont(
            "Arial",
            size,
            bold=True,
        )

    # ========================================================
    # ASSET PATH
    # ========================================================

    def asset_path(
        self,
        *parts,
    ):

        return os.path.join(
            self.project_root,
            "assets",
            "mahirah",
            "end_game",
            *parts,
        )

    # ========================================================
    # LOAD ASSETS
    # ========================================================

    def load_assets(self):

        # ====================================================
        # BACKGROUND
        # ====================================================

        background_path = self.asset_path(
            "end_game_background.png"
        )

        try:

            image = pygame.image.load(
                background_path
            ).convert()

            self.background = (
                pygame.transform.smoothscale(
                    image,
                    (
                        self.width,
                        self.height,
                    ),
                )
            )

            print(
                "[END SCREEN] Background loaded."
            )

        except (
            pygame.error,
            FileNotFoundError,
        ) as error:

            print(
                "[END SCREEN] Background error:",
                error,
            )

            self.background = pygame.Surface(
                (
                    self.width,
                    self.height,
                )
            )

            self.background.fill(
                self.DARK
            )

        # ====================================================
        # CAT FRAMES
        # ====================================================

        self.cat_frames.clear()

        for number in range(
            1,
            9,
        ):

            frame_path = self.asset_path(
                "cat_wave",
                f"{number:02d}.png",
            )

            try:

                frame = pygame.image.load(
                    frame_path
                ).convert_alpha()

                frame = (
                    pygame.transform.smoothscale(
                        frame,
                        self.cat_size,
                    )
                )

                self.cat_frames.append(
                    frame
                )

                print(
                    f"[END SCREEN] Cat frame "
                    f"{number} loaded."
                )

            except (
                pygame.error,
                FileNotFoundError,
            ) as error:

                print(
                    f"[END SCREEN] Cat frame "
                    f"{number} error:",
                    error,
                )

        print(
            "[END SCREEN] Cat frames loaded:",
            len(self.cat_frames),
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.running = True

        self.result = None

        self.phase = 0

        self.phase_timer = 0.0

        self.elapsed = 0.0

        self.cat_frame_index = 0

        self.cat_frame_timer = 0.0

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        player_name="BARISTA",
        level=3,
        successful_drinks=21,
        xp=0,
        credits=0,
    ):

        self.reset()

        self.player_name = str(
            player_name
        )

        self.final_level = int(
            level
        )

        self.successful_drinks = int(
            successful_drinks
        )

        self.final_xp = int(
            xp
        )

        self.final_credits = int(
            credits
        )

        while self.running:

            dt = (
                self.clock.tick(60)
                / 1000.0
            )

            self.elapsed += dt

            self.phase_timer += dt

            # ------------------------------------------------
            # EVENTS
            # ------------------------------------------------

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False

                    self.result = "quit"

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.running = False

                        self.result = "main_menu"

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        self.handle_click(
                            event.pos
                        )

            # ------------------------------------------------
            # UPDATE
            # ------------------------------------------------

            self.update(
                dt
            )

            # ------------------------------------------------
            # DRAW
            # ------------------------------------------------

            self.draw()

            pygame.display.flip()

        return self.result

    # ========================================================
    # CLICK
    # ========================================================

    def handle_click(
        self,
        mouse_pos,
    ):

        if self.phase < 3:

            return

        if self.play_again_rect.collidepoint(
            mouse_pos
        ):

            self.result = "play_again"

            self.running = False

        elif self.main_menu_rect.collidepoint(
            mouse_pos
        ):

            self.result = "main_menu"

            self.running = False

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        dt,
    ):

        # ====================================================
        # CAT ANIMATION
        # ====================================================

        if (
            self.phase >= 1
            and self.cat_frames
        ):

            self.cat_frame_timer += dt

            if (
                self.cat_frame_timer
                >= self.cat_frame_speed
            ):

                self.cat_frame_timer -= (
                    self.cat_frame_speed
                )

                self.cat_frame_index += 1

                if (
                    self.cat_frame_index
                    >= len(
                        self.cat_frames
                    )
                ):

                    self.cat_frame_index = 0

        # ====================================================
        # PHASES
        # ====================================================

        if self.phase == 0:

            if self.phase_timer >= 2.5:

                self.phase = 1

                self.phase_timer = 0.0

        elif self.phase == 1:

            if self.phase_timer >= 3.5:

                self.phase = 2

                self.phase_timer = 0.0

        elif self.phase == 2:

            if self.phase_timer >= 2.0:

                self.phase = 3

                self.phase_timer = 0.0

    # ========================================================
    # TEXT GLOW
    # ========================================================

    def draw_glowing_text(
        self,
        text,
        font,
        color,
        center,
        glow_color=None,
        glow_strength=3,
    ):

        if glow_color is None:

            glow_color = color

        # ----------------------------------------------------
        # MAIN TEXT
        # ----------------------------------------------------

        main_surface = font.render(
            text,
            True,
            color,
        )

        main_rect = (
            main_surface.get_rect(
                center=center
            )
        )

        # ----------------------------------------------------
        # SOFT GLOW
        # ----------------------------------------------------

        for offset in range(
            glow_strength,
            0,
            -1,
        ):

            alpha = int(
                22 / offset
            )

            glow_surface = font.render(
                text,
                True,
                glow_color,
            )

            glow_surface.set_alpha(
                alpha
            )

            glow_rect = (
                glow_surface.get_rect(
                    center=(
                        center[0] + offset,
                        center[1],
                    )
                )
            )

            self.screen.blit(
                glow_surface,
                glow_rect,
            )

            glow_rect = (
                glow_surface.get_rect(
                    center=(
                        center[0] - offset,
                        center[1],
                    )
                )
            )

            self.screen.blit(
                glow_surface,
                glow_rect,
            )

        # ----------------------------------------------------
        # MAIN TEXT
        # ----------------------------------------------------

        self.screen.blit(
            main_surface,
            main_rect,
        )

    # ========================================================
    # BACKGROUND
    # ========================================================

    def draw_background(self):

        self.screen.blit(
            self.background,
            (
                0,
                0,
            ),
        )

        # ----------------------------------------------------
        # DARKEN ENTIRE BACKGROUND
        # ----------------------------------------------------

        overlay = pygame.Surface(
            (
                self.width,
                self.height,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                4,
                5,
                18,
                105,
            )
        )

        self.screen.blit(
            overlay,
            (
                0,
                0,
            ),
        )

        # ----------------------------------------------------
        # SUBTLE TOP GRADIENT-LIKE DARK AREA
        # ----------------------------------------------------

        top_overlay = pygame.Surface(
            (
                self.width,
                220,
            ),
            pygame.SRCALPHA,
        )

        top_overlay.fill(
            (
                5,
                8,
                25,
                90,
            )
        )

        self.screen.blit(
            top_overlay,
            (
                0,
                0,
            ),
        )

    # ========================================================
    # TOP HEADER
    # ========================================================

    def draw_title(self):

        # ----------------------------------------------------
        # SMALL CAFÉ BRAND
        # ----------------------------------------------------

        brand = self.font_medium.render(
            "CYBERPUNK CAFÉ",
            True,
            self.BRIGHT_CYAN,
        )

        brand_rect = brand.get_rect(
            center=(
                self.width // 2,
                48,
            )
        )

        # Dark backing.

        backing = pygame.Rect(
            brand_rect.x - 28,
            brand_rect.y - 10,
            brand_rect.width + 56,
            brand_rect.height + 20,
        )

        pygame.draw.rect(
            self.screen,
            (
                7,
                11,
                28,
            ),
            backing,
            border_radius=15,
        )

        pygame.draw.rect(
            self.screen,
            self.CYAN,
            backing,
            width=1,
            border_radius=15,
        )

        self.screen.blit(
            brand,
            brand_rect,
        )

        # ----------------------------------------------------
        # NEON DIVIDER
        # ----------------------------------------------------

        pygame.draw.line(
            self.screen,
            self.PURPLE,
            (
                370,
                82,
            ),
            (
                910,
                82,
            ),
            2,
        )

        # Small neon points.

        pygame.draw.circle(
            self.screen,
            self.PINK,
            (
                355,
                82,
            ),
            3,
        )

        pygame.draw.circle(
            self.screen,
            self.CYAN,
            (
                925,
                82,
            ),
            3,
        )

    # ========================================================
    # CLOSING MESSAGE
    # ========================================================

    def draw_closing_message(self):

        if self.phase != 0:

            return

        # ----------------------------------------------------
        # DARK TITLE PANEL
        # ----------------------------------------------------

        panel = pygame.Rect(
            275,
            105,
            730,
            125,
        )

        pygame.draw.rect(
            self.screen,
            (
                7,
                10,
                27,
            ),
            panel,
            border_radius=24,
        )

        pygame.draw.rect(
            self.screen,
            self.PURPLE,
            panel,
            width=2,
            border_radius=24,
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        self.draw_glowing_text(
            "THE LAST ORDER HAS BEEN SERVED",
            self.font_title,
            self.WHITE,
            (
                self.width // 2,
                145,
            ),
            self.CYAN,
        )

        subtitle = self.font_small.render(
            "The café is closing for tonight.",
            True,
            self.SOFT_WHITE,
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    self.width // 2,
                    188,
                )
            ),
        )

    # ========================================================
    # CAT
    # ========================================================

    def draw_cat(self):

        if not self.cat_frames:

            return

        frame = self.cat_frames[
            self.cat_frame_index
        ]

        # ----------------------------------------------------
        # FLOATING MOTION
        # ----------------------------------------------------

        bob = int(
            math.sin(
                self.elapsed * 2.5
            ) * 5
        )

        x = (
            self.cat_position[0]
            - frame.get_width() // 2
        )

        y = (
            self.cat_position[1]
            - frame.get_height() // 2
            + bob
        )

        # ----------------------------------------------------
        # SOFT GLOW BEHIND CAT
        # ----------------------------------------------------

        glow_size = 365

        glow = pygame.Surface(
            (
                glow_size,
                glow_size,
            ),
            pygame.SRCALPHA,
        )

        pulse = (
            math.sin(
                self.elapsed * 2.5
            )
            + 1
        ) / 2

        alpha = int(
            25 + pulse * 18
        )

        pygame.draw.ellipse(
            glow,
            (
                120,
                90,
                255,
                alpha,
            ),
            glow.get_rect(),
        )

        self.screen.blit(
            glow,
            (
                x - 17,
                y - 17,
            ),
        )

        # ----------------------------------------------------
        # CAT
        # ----------------------------------------------------

        self.screen.blit(
            frame,
            (
                x,
                y,
            ),
        )

    # ========================================================
    # BYEEEE SPEECH BUBBLE
    # ========================================================

    def draw_bye_bubble(self):

        if self.phase < 1:

            return

        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

        bubble = pygame.Rect(
            80,
            205,
            325,
            100,
        )

        # ----------------------------------------------------
        # SHADOW
        # ----------------------------------------------------

        shadow = pygame.Surface(
            (
                bubble.width + 18,
                bubble.height + 18,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            shadow,
            (
                0,
                0,
                0,
                120,
            ),
            shadow.get_rect(),
            border_radius=26,
        )

        self.screen.blit(
            shadow,
            (
                bubble.x - 9,
                bubble.y + 7,
            ),
        )

        # ----------------------------------------------------
        # BUBBLE
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            self.PANEL,
            bubble,
            border_radius=25,
        )

        pygame.draw.rect(
            self.screen,
            self.PINK,
            bubble,
            width=3,
            border_radius=25,
        )

        # ----------------------------------------------------
        # BYEEEE
        # ----------------------------------------------------

        self.draw_glowing_text(
            "BYEEEE!!",
            self.font_large,
            self.WHITE,
            bubble.center,
            self.PINK,
        )

        # ----------------------------------------------------
        # TAIL
        # ----------------------------------------------------

        pygame.draw.polygon(
            self.screen,
            self.PANEL,
            [
                (
                    bubble.centerx - 15,
                    bubble.bottom - 2,
                ),
                (
                    bubble.centerx + 16,
                    bubble.bottom - 2,
                ),
                (
                    bubble.centerx,
                    bubble.bottom + 27,
                ),
            ],
        )

        pygame.draw.line(
            self.screen,
            self.PINK,
            (
                bubble.centerx - 15,
                bubble.bottom - 1,
            ),
            (
                bubble.centerx,
                bubble.bottom + 27,
            ),
            2,
        )

        pygame.draw.line(
            self.screen,
            self.PINK,
            (
                bubble.centerx,
                bubble.bottom + 27,
            ),
            (
                bubble.centerx + 16,
                bubble.bottom - 1,
            ),
            2,
        )

    # ========================================================
    # THANK YOU
    # ========================================================

    def draw_thank_you(self):

        if self.phase < 2:

            return

        # ----------------------------------------------------
        # DARK BACKING
        # ----------------------------------------------------

        panel = pygame.Rect(
            445,
            100,
            730,
            105,
        )

        pygame.draw.rect(
            self.screen,
            (
                7,
                10,
                27,
            ),
            panel,
            border_radius=22,
        )

        pygame.draw.rect(
            self.screen,
            self.CYAN,
            panel,
            width=2,
            border_radius=22,
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        self.draw_glowing_text(
            "THANK YOU FOR PLAYING!",
            self.font_title,
            self.WHITE,
            (
                panel.centerx,
                138,
            ),
            self.CYAN,
        )

        # ----------------------------------------------------
        # SUBTITLE
        # ----------------------------------------------------

        subtitle = self.font_small.render(
            "See you again at Cyberpunk Café.",
            True,
            self.SOFT_WHITE,
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    panel.centerx,
                    177,
                )
            ),
        )

    # ========================================================
    # STATISTICS PANEL
    # ========================================================

    def draw_statistics(self):

        if self.phase < 3:

            return

        # ----------------------------------------------------
        # MAIN PANEL
        # ----------------------------------------------------

        panel = pygame.Rect(
            620,
            215,
            560,
            340,
        )

        # ----------------------------------------------------
        # SHADOW
        # ----------------------------------------------------

        shadow = pygame.Surface(
            (
                panel.width + 20,
                panel.height + 20,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            shadow,
            (
                0,
                0,
                0,
                145,
            ),
            shadow.get_rect(),
            border_radius=25,
        )

        self.screen.blit(
            shadow,
            (
                panel.x - 10,
                panel.y + 8,
            ),
        )

        # ----------------------------------------------------
        # PANEL
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            self.PANEL,
            panel,
            border_radius=25,
        )

        pygame.draw.rect(
            self.screen,
            self.PURPLE,
            panel,
            width=2,
            border_radius=25,
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        self.draw_glowing_text(
            "FINAL CAFÉ STATISTICS",
            self.font_large,
            self.GOLD,
            (
                panel.centerx,
                panel.y + 42,
            ),
            self.GOLD,
        )

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------

        player_text = self.font_small.render(
            self.player_name.upper(),
            True,
            self.SOFT_WHITE,
        )

        self.screen.blit(
            player_text,
            player_text.get_rect(
                center=(
                    panel.centerx,
                    panel.y + 73,
                )
            ),
        )

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        rows = [
            (
                "SUCCESSFUL DRINKS",
                f"{self.successful_drinks} / 21",
                self.PINK,
            ),
            (
                "FINAL LEVEL",
                f"LEVEL {self.final_level}",
                self.CYAN,
            ),
            (
                "TOTAL XP",
                str(self.final_xp),
                self.PURPLE,
            ),
            (
                "CREDITS EARNED",
                f"${self.final_credits}",
                self.GOLD,
            ),
        ]

        start_y = (
            panel.y + 105
        )

        for index, (
            label,
            value,
            accent,
        ) in enumerate(rows):

            y = (
                start_y
                + index * 53
            )

            # ------------------------------------------------
            # DIVIDER
            # ------------------------------------------------

            if index > 0:

                pygame.draw.line(
                    self.screen,
                    (
                        55,
                        61,
                        90,
                    ),
                    (
                        panel.x + 35,
                        y - 10,
                    ),
                    (
                        panel.right - 35,
                        y - 10,
                    ),
                    1,
                )

            # ------------------------------------------------
            # LABEL
            # ------------------------------------------------

            label_surface = (
                self.font_small.render(
                    label,
                    True,
                    self.SOFT_WHITE,
                )
            )

            self.screen.blit(
                label_surface,
                (
                    panel.x + 35,
                    y,
                ),
            )

            # ------------------------------------------------
            # VALUE
            # ------------------------------------------------

            value_surface = (
                self.font_stat.render(
                    value,
                    True,
                    accent,
                )
            )

            self.screen.blit(
                value_surface,
                value_surface.get_rect(
                    midright=(
                        panel.right - 35,
                        y + 10,
                    )
                ),
            )

    # ========================================================
    # BUTTON
    # ========================================================

    def draw_button(
        self,
        rect,
        label,
        accent,
        hovered,
    ):

        # ----------------------------------------------------
        # HOVER
        # ----------------------------------------------------

        if hovered:

            fill = (
                31,
                27,
                57,
            )

        else:

            fill = (
                10,
                14,
                34,
            )

        # ----------------------------------------------------
        # BUTTON
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=16,
        )

        # ----------------------------------------------------
        # BORDER
        # ----------------------------------------------------

        pygame.draw.rect(
            self.screen,
            accent,
            rect,
            width=2,
            border_radius=16,
        )

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        self.draw_glowing_text(
            label,
            self.font_button,
            self.WHITE,
            rect.center,
            accent,
            glow_strength=2,
        )

    # ========================================================
    # BUTTONS
    # ========================================================

    def draw_buttons(self):

        if self.phase < 3:

            return

        mouse_pos = (
            pygame.mouse.get_pos()
        )

        self.draw_button(
            self.play_again_rect,
            "PLAY AGAIN",
            self.PINK,
            self.play_again_rect.collidepoint(
                mouse_pos
            ),
        )

        self.draw_button(
            self.main_menu_rect,
            "MAIN MENU",
            self.CYAN,
            self.main_menu_rect.collidepoint(
                mouse_pos
            ),
        )

    # ========================================================
    # DRAW EVERYTHING
    # ========================================================

    def draw(self):

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        self.draw_background()

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        self.draw_title()

        # ----------------------------------------------------
        # PHASE 0
        # ----------------------------------------------------

        self.draw_closing_message()

        # ----------------------------------------------------
        # PHASE 1+
        # ----------------------------------------------------

        if self.phase >= 1:

            self.draw_cat()

            self.draw_bye_bubble()

        # ----------------------------------------------------
        # PHASE 2+
        # ----------------------------------------------------

        self.draw_thank_you()

        # ----------------------------------------------------
        # PHASE 3
        # ----------------------------------------------------

        self.draw_statistics()

        self.draw_buttons()